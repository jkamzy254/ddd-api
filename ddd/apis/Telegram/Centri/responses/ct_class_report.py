"""
CT Attendance — class notes and the class report for Telegram (sql/38).

Put this file next to ct_attendance.py and route, in urls.py:

    from .ct_class_report import (CTClassNoteViewSet, CTClassReportViewSet,
                                  CTTelegramAnswerViewSet)

    path('ctClassNote/',       CTClassNoteViewSet.as_view()),
    path('ctClassReport/',     CTClassReportViewSet.as_view()),
    path('ctTelegramAnswer/',  CTTelegramAnswerViewSet.as_view()),   # needs X-Sync-Key (the bot worker)

    GET  ctClassNote/    ?CTDayID= &UID=          the day's notes, CanEdit and CanReport for UID
    POST ctClassNote/    { ActorUID, CTDayID, Objectives, StudentResponse, Problems }
    GET  ctClassReport/  ?CTDayID= &UID=          { Ok, Res, Text, Linked, CanSend, GroupTitle }
    POST ctClassReport/  { ActorUID, CTDayID, To }  To 'me' (default): ActorUID's own chat;
                                                    'group': the session's linked group
    POST ctTelegramAnswer/  from the bot worker: a button press or a command

Settings (settings.py or the environment). Each falls back to Church
Regrouping's, so on the same server and bot nothing new is needed:
    CENTRI_BOT_TOKEN   
    APPS_SCRIPT_SYNC_KEY    ->    (the bot worker sends it as X-Sync-Key)

In Telegram
-----------
Who: the member whose active dbo.TelegramID row is the Telegram account.
What they may see is decided in SQL, as for the page: a session's GSN or
Main JDSN, and admins and CT Leadership (TID 11, PID 200+) for every session.

    /ctreport   (private chat) the running sessions they may see; a session opens
                its latest report, with ◀ ▶ through its classes, 📅 a list of
                them, ⬅ back to the sessions, and 📤 post to its group.
    /ctgroup    (in a group, with the bot added) the sessions they may see, to
                tap: ✅ the session's reports now go to this group; tap again to
                unlink. A session reports to one group; a group takes many.

A report posted to a group has only 🔄 Refresh, so nobody pages it away from
the class it was posted for.

callback_data (64 bytes at most):
    ctr:<CTDayID>          that class's report (Refresh; ◀ ▶)
    ctr:s                  the session list
    ctr:r:<CTID>           the session's latest report
    ctr:l:<CTID>:<page>    the session's classes, 8 a page, newest first
    ctr:p:<CTDayID>        ask to post to the session's group
    ctr:pc:<CTDayID>       post it          ctr:px:<CTDayID>  don't
    ctr:g:<CTID>           (group) link or unlink this group      ctr:gd  done

Every value is bound with %s. Nothing from the request is formatted into SQL.
"""

import datetime
import hmac
import json
import os
import re
import urllib.error
import urllib.request

from django.conf import settings
from django.db import connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


PREFIX = 'ctr:'
TELEGRAM_LIMIT = 4096


def call_proc(sql, params):
    """Runs a stored procedure and returns its first result set as dicts."""
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        if cursor.description is None:
            return []
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def _setting(*names):
    for name in names:
        value = getattr(settings, name, None) or os.environ.get(name)
        if value:
            return value
    return None


def _int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def sync_key_ok(request):
    expected = _setting('APPS_SCRIPT_SYNC_KEY', '')
    given = request.headers.get('X-Sync-Key') or ''
    return bool(expected) and hmac.compare_digest(str(expected), str(given))


# --- the report text -------------------------------------------------------------------

def _date(value):
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _pct(part, whole):
    return int(part * 100.0 / whole + 0.5) if whole else 0


def _frac(part, whole):
    return '%d/%d (%d%%)' % (part, whole, _pct(part, whole))


def _attendance(reg, unreg):
    """'21/32 (66%) +2/6 (33%)': registered, then unregistered when there are any."""
    parts = []
    if reg[1]:
        parts.append(_frac(*reg))
    if unreg[1]:
        parts.append('+' + _frac(*unreg))
    return ' '.join(parts) or '0/0 (0%)'


def _tally(students):
    return (sum(1 for s in students if s.get('Attended')), len(students))


def _hr_labels(students):
    """TGWID -> label: the JDSN's initials, or their name where two share initials."""
    names = {}
    for s in students:
        tgw = s.get('TGWID')
        if tgw and tgw not in names:
            names[tgw] = ((s.get('HR') or '').strip(), (s.get('JDSN') or '').strip() or tgw)
    seen = {}
    for initials, _ in names.values():
        if initials:
            seen[initials] = seen.get(initials, 0) + 1
    return {tgw: initials if initials and seen[initials] == 1 else name
            for tgw, (initials, name) in names.items()}


def _absentees(title, students):
    lines = ['🔻%s: %d' % (title, len(students))]
    for n, s in enumerate(sorted(students, key=lambda x: (x.get('Name') or '').lower()), 1):
        reason = (s.get('LastReason') or '').strip()
        lines.append('%d. %s%s' % (n, s.get('Name') or s.get('UID'), ' (%s)' % reason if reason else ''))
    return lines


def _split_absent(students, long_term):
    absent = [s for s in students if not s.get('Attended')]
    short = [s for s in absent if (s.get('Streak') or 0) < long_term]
    long_ = [s for s in absent if (s.get('Streak') or 0) >= long_term]
    return short, long_


def build_report(row):
    """The report text from spCTClassReport's row."""
    students = row.get('Students') or []
    if isinstance(students, str):
        students = json.loads(students or '[]')
    long_term = row.get('LongTerm') or 6

    reg = [s for s in students if s.get('Counted', True)]
    unreg = [s for s in students if not s.get('Counted', True)]
    day = _date(row.get('CTDate'))

    out = [
        '[%s Report]' % (row.get('SessionName') or 'CT'),
        'Date: %s' % (day.strftime('%A, %d/%m/%y') if day else ''),
        'Title: %s' % ((row.get('Topic') or '').strip() or '-'),
        '',
        '🌟Summary',
        '╰➤Total Attendance: %s' % _attendance(_tally(reg), _tally(unreg)),
        '╰➤Total New Students: %d' % sum(1 for s in reg if not s.get('IsRepeater')),
        '╰➤Total Registered Repeaters: %d' % sum(1 for s in reg if s.get('IsRepeater')),
        '',
        '🔻Attendance per HR',
    ]

    labels = _hr_labels(students)
    groups = {}
    for s in students:
        groups.setdefault(labels.get(s.get('TGWID')) or 'No HR', []).append(s)
    for label in sorted(groups, key=lambda k: (k == 'No HR', k.lower())):
        g = groups[label]
        out.append('╰➤%s: %s' % (label, _attendance(_tally([s for s in g if s.get('Counted', True)]),
                                                      _tally([s for s in g if not s.get('Counted', True)]))))

    short, long_ = _split_absent(reg, long_term)
    out += [''] + _absentees('Short term absentee', short)
    out += [''] + _absentees('Long term absentee', long_)

    if unreg:
        short, long_ = _split_absent(unreg, long_term)
        out += ['', '🌟Unregistered Student Summary',
                '╰➤Total Attendance: %s' % _frac(*_tally(unreg))]
        out += [''] + _absentees('Short term absentee', short)
        out += [''] + _absentees('Long term absentee', long_)

    objectives = [o.strip() for o in (row.get('Objectives') or '').splitlines() if o.strip()]
    if objectives:
        out += ['', '🔹Objectives:'] + ['%d. %s' % (n, o) for n, o in enumerate(objectives, 1)]

    out += ['', '🔹Student’s response:']
    if (row.get('StudentResponse') or '').strip():
        out.append(row['StudentResponse'].strip())
    out += ['', '🔹Problems and solutions in the management of class:']
    if (row.get('Problems') or '').strip():
        out.append(row['Problems'].strip())

    return '\n'.join(out)


def split_text(text, limit=TELEGRAM_LIMIT):
    """Telegram takes 4096 characters a message: split on line ends."""
    chunks, cur = [], ''
    for line in text.split('\n'):
        while len(line) > limit:
            if cur:
                chunks.append(cur)
                cur = ''
            chunks.append(line[:limit])
            line = line[limit:]
        candidate = line if not cur else cur + '\n' + line
        if len(candidate) > limit:
            chunks.append(cur)
            cur = line
        else:
            cur = candidate
    if cur or not chunks:
        chunks.append(cur)
    return chunks


def _short(value):
    d = _date(value)
    return d.strftime('%a %d/%m') if d else ''


def _clip(text, n):
    text = str(text or '')
    return text if len(text) <= n else text[:n - 1] + '…'


def _btn(text, data):
    return {'text': text, 'callback_data': PREFIX + data}


def keyboard(row, private=True):
    """In a private chat: ◀ previous · 🔄 refresh · next ▶, then 📅 the session's
       classes and ⬅ the sessions, and 📤 post to the group when it has one.
       In a group: 🔄 only, so nobody pages the posted report to another class."""
    day = row['CTDayID']
    if not private:
        return [[_btn('🔄 Refresh', str(day))]]

    nav = []
    if row.get('PrevDayID'):
        nav.append(_btn('◀ ' + _short(row.get('PrevDate')), str(row['PrevDayID'])))
    nav.append(_btn('🔄 Refresh', str(day)))
    if row.get('NextDayID'):
        nav.append(_btn(_short(row.get('NextDate')) + ' ▶', str(row['NextDayID'])))

    rows = [nav, [_btn('📅 Classes', 'l:%s:0' % row['CTID']), _btn('⬅ Sessions', 's')]]
    if row.get('GroupChatID'):
        rows.append([_btn('📤 Post to ' + _clip(row.get('GroupTitle') or 'the group', 40), 'p:%s' % day)])
    return rows


def report_row(actor_uid, ct_day_id):
    rows = call_proc("EXEC spCTClassReport @ActorUID = %s, @CTDayID = %s", [actor_uid, ct_day_id])
    return rows[0] if rows else {'Ok': 0, 'Res': 'No CT day with that ID.'}


# --- Telegram ----------------------------------------------------------------------------

def _bot_token():
    return _setting('CENTRI_BOT_TOKEN', '')


def _telegram(method, body):
    """Calls the Bot API: (ok, result or Telegram's reason, parameters). Never raises."""
    token = _bot_token()
    if not token:
        return False, 'The server has no Telegram bot token set.', {}
    try:
        req = urllib.request.Request(
            'https://api.telegram.org/bot%s/%s' % (token, method),
            data=json.dumps(body).encode('utf-8'),
            headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as res:
            out = json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        # Telegram answers a refusal with 400/403 and a JSON reason.
        try:
            out = json.loads(e.read().decode('utf-8'))
        except ValueError:
            out = {'description': 'HTTP %s' % e.code}
    except Exception as e:
        print('CT Attendance - Telegram %s failed:' % method, e)
        return False, str(e), {}
    if out.get('ok'):
        return True, out.get('result'), {}
    print('CT Attendance - Telegram %s refused:' % method, out.get('description'))
    return False, out.get('description') or 'no reason given', out.get('parameters') or {}


def _group_moved(old_id, new_id):
    """A group upgraded to a supergroup gets a new chat ID: follow it."""
    with connection.cursor() as cursor:
        cursor.execute("UPDATE dbo.CTSessionTelegramTable SET ChatID = %s WHERE ChatID = %s",
                       [int(new_id), int(old_id)])


def send_report(chat_id, row, private=True):
    """Sends the report to chat_id, in as many messages as it takes; the buttons go
       on the last. Returns (sent, total, Telegram's reason for the last failure)."""
    chunks = split_text(build_report(row))
    kb = keyboard(row, private)
    sent, error = 0, None
    for n, text in enumerate(chunks, 1):
        body = {'chat_id': str(chat_id), 'text': text, 'disable_web_page_preview': True}
        if n == len(chunks):
            body['reply_markup'] = {'inline_keyboard': kb}
        ok, info, params = _telegram('sendMessage', body)
        if not ok and params.get('migrate_to_chat_id'):
            _group_moved(chat_id, params['migrate_to_chat_id'])
            chat_id = params['migrate_to_chat_id']
            body['chat_id'] = str(chat_id)
            ok, info, params = _telegram('sendMessage', body)
        if ok:
            sent += 1
        else:
            error = info
    return sent, len(chunks), error


def _group_problem(error, title):
    e = (error or '').lower()
    if any(k in e for k in ('not found', 'kicked', 'not a member', 'forbidden')):
        return 'The bot is not in %s any more. Add it back, then send /ctgroup there.' % title
    if 'rights' in e or 'not enough' in e:
        return 'The bot may not post in %s. Allow it to send messages there.' % title
    return 'Telegram did not take the report (%s).' % (error or 'no reason given')


# --- Telegram: what each command and button shows ------------------------------------------

PAGE = 8


def _ans(toast=None, text=None, kb=None, ok=True, alert=False, kb_only=False):
    """What the bot worker does: a pop-up (Toast), then replaces the message's
       Text and Keyboard (Text None: leaves it), or only its Keyboard (KeyboardOnly)."""
    return {'Ok': ok, 'Toast': toast, 'Alert': alert, 'Text': text, 'Keyboard': kb, 'KeyboardOnly': kb_only}


def _refuse(message):
    return _ans(message, ok=False, alert=True)


def sessions_view(uid):
    rows = call_proc("EXEC spCTReportSessions @UID = %s", [uid])
    if not rows:
        return 'There are no running sessions whose class reports you can see.', []
    kb = [[_btn('%s · %s' % (_clip(r['Label'], 44), _short(r.get('LastDate')) or 'no classes yet'),
                'r:%s' % r['CTID'])] for r in rows[:90]]
    return '📊 Class reports. Choose a session:', kb


def classes_view(uid, ctid, page):
    rows = call_proc("EXEC spCTReportClasses @UID = %s, @CTID = %s", [uid, ctid])
    back = [_btn('⬅ Sessions', 's')]
    if not rows:
        return 'No held classes to report on in this session.', [back]

    pages = (len(rows) + PAGE - 1) // PAGE
    page = max(0, min(page, pages - 1))
    kb = [[_btn('%s · %s' % (_short(r['CTDate']), _clip((r.get('Topic') or '').strip() or 'No title', 36)),
                str(r['ID']))] for r in rows[page * PAGE:(page + 1) * PAGE]]
    nav = []
    if page > 0:
        nav.append(_btn('◀ Newer', 'l:%s:%d' % (ctid, page - 1)))
    if page < pages - 1:
        nav.append(_btn('Older ▶', 'l:%s:%d' % (ctid, page + 1)))
    if nav:
        kb.append(nav)
    kb.append(back)
    return ('%s: %d class%s held. Choose one:%s'
            % (rows[0]['Label'], len(rows), '' if len(rows) == 1 else 'es',
               ' (page %d of %d)' % (page + 1, pages) if pages > 1 else '')), kb


def group_view(uid, chat_id, note=None):
    rows = call_proc("EXEC spCTReportSessions @UID = %s", [uid])
    if not rows:
        return (note + '\n\n' if note else '') + 'There are no running sessions you can link to a group.', []
    kb = [[_btn(('✅ ' if str(r.get('GroupChatID') or '') == str(chat_id) else '') + _clip(r['Label'], 50),
                'g:%s' % r['CTID'])] for r in rows[:90]]
    kb.append([_btn('Done', 'gd')])
    text = ('Which sessions post their class reports to this group? Tap one to link or unlink it.\n'
            '✅ = posts here. A session posts to one group, so linking it here moves it from any other.')
    return (note + '\n\n' + text if note else text), kb


def group_done(uid, chat_id):
    rows = call_proc("EXEC spCTReportSessions @UID = %s", [uid])
    here = [r['Label'] for r in rows if str(r.get('GroupChatID') or '') == str(chat_id)]
    return (('Class reports of %s are posted to this group.' % ', '.join(here)) if here
            else 'No sessions post their class reports to this group.') + ' Send /ctgroup to change.'


def show_report(uid, day_id, chat_id, private):
    row = report_row(uid, day_id)
    if not row.get('Ok'):
        return _refuse(row.get('Res') or 'That report is not available.')
    chunks = split_text(build_report(row))
    if len(chunks) == 1:
        return _ans(text=chunks[0], kb=keyboard(row, private))
    sent, total, _ = send_report(chat_id, row, private)
    return _ans('Too long for one message, so it was sent again below.' if sent == total
                else 'Telegram did not take the whole report. Please use the app.',
                ok=sent == total, alert=True)


def telegram_press(uid, data, chat_id, private, chat_title=None):
    m = re.fullmatch(r'ctr:(\d+)', data)
    if m:
        return show_report(uid, int(m.group(1)), chat_id, private)

    if private:
        if data == 'ctr:s':
            text, kb = sessions_view(uid)
            return _ans(text=text, kb=kb)

        m = re.fullmatch(r'ctr:r:(\d+)', data)
        if m:
            rows = call_proc("EXEC spCTReportClasses @UID = %s, @CTID = %s", [uid, int(m.group(1))])
            if not rows:
                return _refuse('That session has no held classes to report on yet.')
            return show_report(uid, rows[0]['ID'], chat_id, True)

        m = re.fullmatch(r'ctr:l:(\d+):(\d+)', data)
        if m:
            text, kb = classes_view(uid, int(m.group(1)), int(m.group(2)))
            return _ans(text=text, kb=kb)

        m = re.fullmatch(r'ctr:(p|pc|px):(\d+)', data)
        if m:
            step, day = m.group(1), int(m.group(2))
            row = report_row(uid, day)
            if not row.get('Ok'):
                return _refuse(row.get('Res') or 'That report is not available.')
            title = row.get('GroupTitle') or 'the group'
            if step == 'px' or not row.get('GroupChatID'):
                return _ans(None if row.get('GroupChatID') else 'This session no longer has a group.',
                            kb=keyboard(row), kb_only=True)
            if step == 'p':
                # A second tap to post, so a stray tap does not put it in front of the group.
                return _ans('Post this report to %s?' % title, kb_only=True,
                            kb=[[_btn('✅ Yes, post to ' + _clip(title, 30), 'pc:%s' % day),
                                 _btn('✖ Cancel', 'px:%s' % day)]])
            sent, total, error = send_report(row['GroupChatID'], row, private=False)
            return _ans('Posted to %s.' % title if sent == total else _group_problem(error, title),
                        ok=sent == total, alert=sent != total, kb=keyboard(row), kb_only=True)
    else:
        m = re.fullmatch(r'ctr:g:(\d+)', data)
        if m:
            rows = call_proc("EXEC spCTSessionGroupLink @ActorUID = %s, @CTID = %s, @ChatID = %s, @ChatTitle = %s",
                             [uid, int(m.group(1)), int(chat_id), chat_title or None])
            res = rows[0] if rows else {'Ok': 0, 'Res': 'No response.'}
            if not res.get('Ok'):
                return _refuse(res.get('Res'))
            text, kb = group_view(uid, chat_id)
            return _ans(_clip(res.get('Res'), 190), text=text, kb=kb)
        if data == 'ctr:gd':
            return _ans(text=group_done(uid, chat_id), kb=[])

    return _refuse('This button only works in %s.' % ('a group' if private else 'a private chat with me'))


def telegram_command(uid, command, chat_id, private):
    if command == 'ctreport':
        if not private:
            return {'Ok': True, 'Text': 'Send /ctreport to me in a private chat, so the reports reach only you. '
                                        'To post them here, send /ctgroup.'}
        text, kb = sessions_view(uid)
    elif command == 'ctgroup':
        if private:
            return {'Ok': True, 'Text': 'Add me to the group first, then send /ctgroup there to choose which '
                                        'sessions post their class reports to it.'}
        text, kb = group_view(uid, chat_id)
    else:
        return {'Ok': False, 'Text': 'I know /ctreport and /ctgroup.'}
    return {'Ok': True, 'Text': text, 'Keyboard': kb}


# --- views ------------------------------------------------------------------------------

def _error(e):
    print('CT Attendance - class report:', e)
    return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _ok(body):
    return Response(body, status=status.HTTP_200_OK)


class CTClassNoteViewSet(APIView):
    """A CT day's objectives, students' response, and problems and solutions."""

    def get(self, request):
        try:
            rows = call_proc("EXEC spCTClassNote @ActorUID = %s, @CTDayID = %s",
                             [request.GET.get('UID'), _int(request.GET.get('CTDayID'))])
            return _ok(rows)
        except Exception as e:
            return _error(e)

    def post(self, request):
        rec = request.data
        try:
            rows = call_proc(
                "EXEC spCTClassNoteSave @ActorUID = %s, @CTDayID = %s, "
                "@Objectives = %s, @StudentResponse = %s, @Problems = %s",
                [rec.get('ActorUID'), _int(rec.get('CTDayID')),
                 rec.get('Objectives') or None, rec.get('StudentResponse') or None,
                 rec.get('Problems') or None])
            return _ok(rows[0] if rows else {'Res': 'No response', 'Ok': 0})
        except Exception as e:
            return _error(e)


class CTClassReportViewSet(APIView):
    """GET: the report's text, to preview. POST: send it to the actor's own chat (To 'me')
       or to the session's group (To 'group')."""

    def get(self, request):
        try:
            row = report_row(request.GET.get('UID'), _int(request.GET.get('CTDayID')))
            if not row.get('Ok'):
                return _ok({'Ok': 0, 'Res': row.get('Res')})
            return _ok({'Ok': 1, 'CTDayID': row.get('CTDayID'), 'Text': build_report(row),
                        'Linked': bool(row.get('TelID')), 'CanSend': bool(_bot_token()),
                        'GroupTitle': (row.get('GroupTitle') or 'the group') if row.get('GroupChatID') else None})
        except Exception as e:
            return _error(e)

    def post(self, request):
        rec = request.data
        try:
            row = report_row(rec.get('ActorUID'), _int(rec.get('CTDayID')))
            if not row.get('Ok'):
                return _ok({'Ok': 0, 'Res': row.get('Res')})
            if not _bot_token():
                return _ok({'Ok': 0, 'Res': 'The server has no Telegram bot token set.'})

            if str(rec.get('To') or 'me').lower() == 'group':
                if not row.get('GroupChatID'):
                    return _ok({'Ok': 0, 'Res': 'This session has no Telegram group yet. Add the bot to the group '
                                                'and send /ctgroup there.'})
                title = row.get('GroupTitle') or 'the group'
                sent, total, error = send_report(row['GroupChatID'], row, private=False)
                if sent == total:
                    return _ok({'Ok': 1, 'Res': 'Posted to %s%s.' % (title, '' if total == 1 else ' in %d messages' % total)})
                return _ok({'Ok': 0, 'Res': _group_problem(error, title) if not sent
                            else 'Only %d of %d messages reached %s.' % (sent, total, title)})

            if not row.get('TelID'):
                return _ok({'Ok': 0, 'Res': 'Your account has no Telegram linked, so there is nowhere to send it. '
                                            'Copy the report instead.'})
            sent, total, error = send_report(row['TelID'], row)
            if sent == total:
                return _ok({'Ok': 1, 'Res': 'Sent to your Telegram.' if total == 1
                            else 'Sent to your Telegram in %d messages.' % total})
            return _ok({'Ok': 0, 'Res': 'Telegram did not take the report. Start a chat with the bot first, '
                                        'then try again.' if not sent
                        else 'Only %d of %d messages reached Telegram.' % (sent, total)})
        except Exception as e:
            return _error(e)


class CTTelegramAnswerViewSet(APIView):
    """
    From the bot worker (X-Sync-Key), a button press or a command:
        { "TelegramUserID": <from.id>, "Data": "ctr:...",   "ChatID", "ChatType", "ChatTitle" }
        { "TelegramUserID": <from.id>, "Command": "ctreport" | "ctgroup", "ChatID", "ChatType", "ChatTitle" }
    A press is answered { Ok, Toast, Alert, Text, Keyboard, KeyboardOnly } (see _ans); a
    command { Ok, Text, Keyboard }, sent as a reply. Without ChatType (an older worker) the
    chat is taken to be the private one.
    """

    def post(self, request):
        if not sync_key_ok(request):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        tel = str(data.get('TelegramUserID') or '').strip()
        press = str(data.get('Data') or '').strip()
        command = str(data.get('Command') or '').strip().lstrip('/').split('@')[0].lower()
        chat_id = _int(data.get('ChatID')) or _int(tel)
        private = str(data.get('ChatType') or 'private') == 'private'

        def refuse(message):
            return _ok(_refuse(message) if press else {'Ok': False, 'Text': message})

        if not tel or not (command or press.startswith(PREFIX)):
            return refuse('This is not something CT Attendance knows.')

        try:
            users = call_proc("EXEC spCTTelegramUser @TelID = %s", [tel])
            uids = {u['UID'] for u in users}
            if not uids:
                return refuse("This Telegram account isn't linked to anyone in CT Attendance.")
            if len(uids) > 1:
                return refuse('This Telegram account is linked to more than one member. Please use the app.')
            uid = uids.pop()

            if command:
                return _ok(telegram_command(uid, command, chat_id, private))
            return _ok(telegram_press(uid, press, chat_id, private, data.get('ChatTitle')))
        except Exception as e:
            print('CT Attendance - Telegram request failed:', e)
            return refuse('The report could not be made. Please try again, or use the app.')
