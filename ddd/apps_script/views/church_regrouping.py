"""
Church Regrouping — Django views for the Apps Script app.

This file is the server's church_regrouping.py, kept ready to copy over the
running one as is. Routes, for urls.py:

    path('churchRegrpGetMember/',      ChurchRegrpGetMemberViewSet.as_view()),
    path('churchRegrpGetContext/',     ChurchRegrpGetContextViewSet.as_view()),
    path('churchRegrpGetGroups/',      ChurchRegrpGetGroupsViewSet.as_view()),
    path('churchRegrpGetTasks/',       ChurchRegrpGetTasksViewSet.as_view()),
    path('churchRegrpGetTaskRefs/',    ChurchRegrpGetTaskRefsViewSet.as_view()),
    path('churchRegrpGetMembers/',     ChurchRegrpGetMembersViewSet.as_view()),
    path('churchRegrpGetRequests/',    ChurchRegrpGetRequestsViewSet.as_view()),
    path('churchRegrpSearchMembers/',  ChurchRegrpSearchMembersViewSet.as_view()),
    path('churchRegrpSaveRequest/',    ChurchRegrpSaveRequestViewSet.as_view()),
    path('churchRegrpNotifyMoves/',    ChurchRegrpNotifyMovesViewSet.as_view()),   # after a save of many
    path('churchRegrpResolve/',        ChurchRegrpResolveViewSet.as_view()),
    path('churchRegrpSetDeptLeader/',  ChurchRegrpSetDeptLeaderViewSet.as_view()),
    path('churchRegrpMoveGroup/',      ChurchRegrpMoveGroupViewSet.as_view()),
    path('churchRegrpGroupHistory/',   ChurchRegrpGroupHistoryViewSet.as_view()),
    path('churchRegrpArchive/',        ChurchRegrpArchiveViewSet.as_view()),
    path('churchRegrpSetGroupRule/',   ChurchRegrpSetGroupRuleViewSet.as_view()),
    path('churchRegrpSetMemberProfile/', ChurchRegrpSetMemberProfileViewSet.as_view()),
    path('churchRegrpProfileHistory/', ChurchRegrpProfileHistoryViewSet.as_view()),
    path('churchRegrpCTGetMembers/',   ChurchRegrpCTGetMembersViewSet.as_view()),
    path('churchRegrpCTGetGroups/',    ChurchRegrpCTGetGroupsViewSet.as_view()),
    path('churchRegrpCTMove/',         ChurchRegrpCTMoveViewSet.as_view()),
    path('churchRegrpCTSetLeader/',    ChurchRegrpCTSetLeaderViewSet.as_view()),
    path('churchRegrpCTHistory/',      ChurchRegrpCTHistoryViewSet.as_view()),
    path('churchRegrpCTSaveGroup/',    ChurchRegrpCTSaveGroupViewSet.as_view()),
    path('churchRegrpGetSubdivisions/', ChurchRegrpGetSubdivisionsViewSet.as_view()),
    path('churchRegrpSetSubdivLeader/', ChurchRegrpSetSubdivLeaderViewSet.as_view()),
    path('churchRegrpSetSubdivRole/',  ChurchRegrpSetSubdivRoleViewSet.as_view()),
    path('churchRegrpSetFeedbackLeader/', ChurchRegrpSetFeedbackLeaderViewSet.as_view()),
    path('churchRegrpSetDeptCategory/', ChurchRegrpSetDeptCategoryViewSet.as_view()),
    path('churchRegrpEditDates/',      ChurchRegrpEditDatesViewSet.as_view()),
    path('churchRegrpGetHistory/',     ChurchRegrpGetHistoryViewSet.as_view()),
    path('churchRegrpMemberSheet/',    ChurchRegrpMemberSheetViewSet.as_view()),   # needs X-Sync-Key
    path('churchRegrpTransferDigest/', ChurchRegrpTransferDigestViewSet.as_view()), # needs X-Sync-Key
    path('churchRegrpTelegramAnswer/', ChurchRegrpTelegramAnswerViewSet.as_view()), # needs X-Sync-Key (the bot worker)

Settings (settings.py or the environment):
    CHURCH_REGRP_SYNC_KEY   shared secret: Apps Script's sheet sync and the bot worker send it as X-Sync-Key
    CHURCH_REGRP_BOT_TOKEN  the Telegram bot's token (falls back to CODEY_BOT_TOKEN); without one nothing is sent
    CHURCH_REGRP_DELETE_AFTER  seconds before the bot deletes a fully answered message (default 120; 0 keeps it)
    CHURCH_REGRP_APP_URL    the web app's /exec link, for the digest's button
                            (messages from a save use the link Apps Script sends)

If the login view you already have is routed somewhere else, either route
this one as above or change ENDPOINTS.member in Code.js.

Every value is bound with %s. Nothing from the request is formatted into SQL.
"""

import json
import os
import re
import threading
import urllib.request

from django.conf import settings
from django.db import close_old_connections, connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


def fetch_rows(cursor):
    """Rows as dicts; [] when the statement returned no result set."""
    if cursor.description is None:
        return []
    columns = [column[0] for column in cursor.description]
    return [dict(zip(columns, record)) for record in cursor.fetchall()]


def blank_to_none(value):
    """A GET parameter or JSON field left empty means NULL, not ''."""
    if value is None:
        return None
    if isinstance(value, str) and value.strip() == '':
        return None
    return value


def sql_error(e):
    """
    The procedures THROW sentences meant for the user, with error numbers
    50000 and up. pyodbc wraps them as
    "... [SQL Server]You do not have access to this department. (50002) (SQLExecDirectW)".
    Only those sentences are passed on. Anything else (a missing object, a
    type error, a lost connection) would show the database's structure, so it
    goes to the server log and the page gets a plain message.
    """
    found = re.findall(r'\[SQL Server\](.*?)\s*\((\d+)\)', str(e))
    if found and int(found[-1][1]) >= 50000:
        return found[-1][0].strip()
    print('Church Regrouping — server error:', e)
    return 'The server could not complete that. Please try again, or tell the administrator if it keeps happening.'


def error_response(e):
    return Response({'error': sql_error(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- Telegram ----------------------------------------------------------------------
#
# Messages are sent from here, straight to the Telegram Bot API, with the bot's
# token (CHURCH_REGRP_BOT_TOKEN). Sending needs nothing from the bot worker on
# Heroku: any number of processes can send with one token.
#
# The buttons are callback buttons. Telegram delivers the press to whoever
# receives the bot's updates (the worker). Its handler (regrouping_handler.py)
# posts the press to churchRegrpTelegramAnswer/ below, which acts as the member
# linked to that Telegram account and answers with the message to show next.
# The callback_data used are listed under "Telegram notices" below.

def link_row(url, text='🔗 See more details'):
    """A keyboard row with one link button; [] without a link."""
    return [{'text': text, 'url': url}] if url else []


def answer_row(request_id, label=''):
    """Accept / Decline buttons for one request ('label' tells rows apart in a digest)."""
    if request_id in (None, ''):
        return []
    return [{'text': '✅ Accept' + label, 'callback_data': 'crg:a:%s' % request_id},
            {'text': '❌ Decline' + label, 'callback_data': 'crg:d:%s' % request_id}]


def telegram_body(tel_id, text, rows=None):
    """The Telegram Bot API sendMessage body, or None when there is no chat to send to
       (no active TelegramID row) or nothing to say. rows: keyboard rows (empty ones dropped)."""
    if not tel_id or not text:
        return None
    body = {'chat_id': str(tel_id), 'text': text, 'disable_web_page_preview': True}
    keyboard = [r for r in (rows or []) if r]
    if keyboard:
        body['reply_markup'] = {'inline_keyboard': keyboard}
    return body


def _bot_token():
    # Codey sends these (its worker receives the button presses); CHURCH_REGRP_BOT_TOKEN overrides.
    return (getattr(settings, 'CHURCH_REGRP_BOT_TOKEN', None) or os.environ.get('CHURCH_REGRP_BOT_TOKEN')
            or os.environ.get('CODEY_BOT_TOKEN'))


def send_telegram(body):
    """Sends one sendMessage body. The sent message (a dict: truthy) when Telegram
       accepted it, else False; never raises."""
    token = _bot_token()
    if not token or not body:
        return False
    try:
        req = urllib.request.Request(
            'https://api.telegram.org/bot%s/sendMessage' % token,
            data=json.dumps(body).encode('utf-8'),
            headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as res:
            out = json.loads(res.read().decode('utf-8'))
        return (out.get('result') or True) if out.get('ok') else False
    except Exception as e:
        print('Church Regrouping - Telegram send failed:', e)
        return False


def send_later(jobs):
    """jobs: [(body, request_ids or None)]. Sent on a background thread so a slow or
       unreachable Telegram never holds up (or fails) the save. Once a body with
       request_ids is delivered, those requests are marked notified, so the transfer
       digest does not send them again."""
    jobs = [j for j in jobs if j and j[0]]
    if not jobs or not _bot_token():
        return

    def run():
        try:
            for body, ids in jobs:
                if send_telegram(body) and ids:
                    mark_transfers_sent(ids)
        except Exception as e:
            print('Church Regrouping - Telegram job failed:', e)
        finally:
            close_old_connections()
            connection.close()

    threading.Thread(target=run, daemon=True).start()


def with_param(url, name, value):
    """url + '&name=value' (or '?'); None stays None."""
    if not url or value in (None, ''):
        return url
    return url + ('&' if '?' in url else '?') + name + '=' + str(value)


# --- Telegram notices: many moves, one message ---------------------------------------------
#
# Regroup -> "Apply changes" saves every member side by side (one churchRegrpSaveRequest
# each, sent with NotifyLater), then Code.js calls churchRegrpNotifyMoves/ ONCE with the
# departments the moves went to. Each receiving department then gets one message (a
# notice) listing every move waiting for it. A single save is told about at once, the
# same way (a notice of one move).
#
#     Hello <Leader>
#
#     10 transfers into your department (D1):
#
#     ⏳ 1. <Member> — D5 G4 → G7
#     ⏳ 2. ...
#
#     10 of 10 waiting for you. Tap a number to see one in full, or answer them all.
#
#     [1] [2] [3] [4] [5]
#     [6] [7] [8] [9] [10]
#     [✅ Accept all (10)] [❌ Decline all (10)]
#     [🔗 See more details]
#
# A number opens that move in full, with Accept / Decline and [◀ 2] [📋 List] [4 ▶];
# answering one goes on to the next still waiting (the list once none are). "Accept all" /
# "Decline all" ask once to confirm, then answer every move still waiting in one go. A
# notice of one move is just that move with Accept / Decline. Over 10 moves, the list pages.
#
# callback_data (Telegram allows 64 bytes; N = NoticeID, R = RequestID, P = page):
#     crg:l:N:P        the list, page P           crg:v:N:R        one move in full
#     crg:one:a:N:R    accept one                 crg:one:d:N:R    decline one
#     crg:ask:a:N      "Accept all?"              crg:ask:d:N      "Decline all?"
#     crg:all:a:N      accept all (confirmed)     crg:all:d:N      decline all (confirmed)
#     crg:a:R, crg:d:R messages from before notices, and the digest's GET — still answered
#
# Every press re-reads the notice (spChurchRegrpNoticeGet), so the message shows each move
# as it stands now: answered on the site, cancelled or sent elsewhere included.
#
# Once nothing in a message waits for an answer, it keeps only the link button, and the
# answer to the worker carries DeleteAfter (CHURCH_REGRP_DELETE_AFTER seconds, default 120):
# the worker then deletes the message. Telegram lets a bot delete its message only in the
# first 48 hours; after that the message stays, without its buttons.

NOTICE_PAGE = 10
_ICONS = {'wait': '⏳', 'accepted': '☑️', 'applied': '✅', 'declined': '❌', 'cancelled': '↩️', 'moved': '↪️'}


def _btn(text, *parts):
    return {'text': text, 'callback_data': 'crg:' + ':'.join(str(p) for p in parts)}


def _date(d):
    if not d:
        return None
    try:
        return d.strftime('%d %b %Y')
    except AttributeError:
        return str(d)[:10]


def notice_rows(notice_id, uid):
    """The notice's moves as they stand now (one row each, the notice's details on every row)."""
    with connection.cursor() as cursor:
        cursor.execute("EXEC spChurchRegrpNoticeGet @NoticeID = %s, @UID = %s", [int(notice_id), uid])
        return fetch_rows(cursor)


def _state(it):
    """wait | accepted (not applied yet) | applied | declined | cancelled | moved (pointed elsewhere)"""
    st = it.get('Status')
    if st == 'Pending':
        if it.get('AwaitingAccept') and it.get('ToDID') == it.get('DID'):
            return 'wait'
        return 'accepted' if it.get('AcceptedBy') else 'moved'
    return {'Applied': 'applied', 'Rejected': 'declined', 'Cancelled': 'cancelled'}.get(st, 'moved')


def _state_line(it):
    s = _state(it)

    def by(name):
        return ' by %s' % name if name else ''

    if s == 'wait':
        return '⏳ Waiting for your answer'
    if s == 'accepted':
        return '☑️ Accepted%s, not applied yet%s' % (by(it.get('AcceptedByName')),
                                                     ': ' + it['Result'] if it.get('Result') else '')
    if s == 'applied':
        return '✅ Applied' + (' (accepted%s)' % by(it.get('AcceptedByName')) if it.get('AcceptedBy') else '')
    if s == 'declined':
        return '❌ ' + (it.get('Result') or 'Declined')
    if s == 'cancelled':
        return '↩️ Cancelled' + by(it.get('ResolvedByName'))
    if it.get('ToGrp') and it.get('ToDID') != it.get('DID'):
        return '↪️ Changed: now going to %s (%s)' % (it['ToGrp'], it.get('ToDept') or '?')
    return '↪️ Changed: no longer waiting for %s' % (it.get('Dept') or 'this department')


def _where(nt):
    dept = nt.get('Dept') or 'the department'
    if nt.get('InChargeAs') in (None, 'Department leader'):
        return 'your department (%s)' % dept
    return '%s (it has no department leader, so this comes to you)' % dept


def _from(it):
    return ' '.join(x for x in (it.get('FromDept'), it.get('FromGrp')) if x) or 'no group'


def _line(it, icon=True):
    return '%s%d. %s — %s → %s' % (_ICONS[_state(it)] + ' ' if icon else '', it['n'],
                                   it.get('Name') or it['RequestID'], _from(it), it.get('ToGrp') or '?')


def _details(it):
    task = it.get('ToTask') if it.get('ToTaskCode') else '%s (no change)' % (it.get('FromTask') or 'Member')
    lines = ['Group: %s (from %s)' % (it.get('ToGrp') or '?', _from(it)),
             'Task: %s' % task,
             'Effective Date: %s' % (_date(it.get('EffectiveDate')) or 'When accepted')]
    if it.get('RequestedByName'):
        lines.append('Requested by: %s' % it['RequestedByName'])
    if it.get('Notes'):
        lines.append('Notes: %s' % it['Notes'])
    return '\n'.join(lines)


def _waiting(items):
    return [it for it in items if _state(it) == 'wait']


def _view(text, keyboard, note=None):
    if note:
        text = note + '\n\n' + text
    return text[:4096], [r for r in keyboard if r]


def notice_list(items, page=0, note=None):
    """(text, keyboard) for the list."""
    nt, nid = items[0], items[0]['NoticeID']
    waiting = _waiting(items)
    # All answered: the whole list at once (up to 60), and no buttons but the link.
    pages = max(1, -(-len(items) // NOTICE_PAGE)) if waiting else 1
    page = min(max(0, page), pages - 1)
    shown = items[page * NOTICE_PAGE:(page + 1) * NOTICE_PAGE] if waiting else items[:60]

    text = ['Hello %s' % (nt.get('ToName') or 'there'), '',
            '%d transfers into %s:' % (len(items), _where(nt)), '']
    text += [_line(it) for it in shown]
    if len(shown) < len(items) and not waiting:
        text.append('… and %d more' % (len(items) - len(shown)))
    text.append('')
    if pages > 1:
        text.append('Page %d of %d' % (page + 1, pages))
    if waiting:
        text.append('%d of %d waiting for you. Tap a number to see one in full, or answer them all.'
                    % (len(waiting), len(items)))
    else:
        text.append('All answered. Thank you!')

    kb = []
    if waiting:
        nums = [_btn(str(it['n']) if _state(it) == 'wait' else '%d %s' % (it['n'], _ICONS[_state(it)]),
                     'v', nid, it['RequestID']) for it in shown]
        kb += [nums[i:i + 5] for i in range(0, len(nums), 5)]
    if pages > 1:
        kb.append([_btn('◀', 'l', nid, (page - 1) % pages),
                   _btn('%d / %d' % (page + 1, pages), 'l', nid, page),
                   _btn('▶', 'l', nid, (page + 1) % pages)])
    if waiting:
        kb.append([_btn('✅ Accept all (%d)' % len(waiting), 'ask', 'a', nid),
                   _btn('❌ Decline all (%d)' % len(waiting), 'ask', 'd', nid)])
    kb.append(link_row(nt.get('Url') or _app_url('Requests')))
    return _view('\n'.join(text), kb, note)


def notice_item(items, request_id, note=None):
    """(text, keyboard) for one move; a notice of one move is only this."""
    nt, nid = items[0], items[0]['NoticeID']
    idx = next((i for i, it in enumerate(items) if str(it['RequestID']) == str(request_id)), None)
    if idx is None:
        return notice_list(items, 0, note)
    it = items[idx]
    waiting = _state(it) == 'wait'

    if len(items) == 1:
        text = ['Hi %s,' % (nt.get('ToName') or 'there'), '',
                'A change has been requested for %s to %s' % (it.get('Name'), _where(nt)), '',
                _details(it), '', _state_line(it)]
        if waiting:
            text += ['', 'Accept or decline with the buttons below. To see more details, please click on the link.']
    else:
        text = ['Transfer %d of %d into %s' % (it['n'], len(items), _where(nt)), '',
                it.get('Name') or '', _details(it), '', _state_line(it)]

    kb = []
    if waiting:
        kb.append([_btn('✅ Accept', 'one', 'a', nid, it['RequestID']),
                   _btn('❌ Decline', 'one', 'd', nid, it['RequestID'])])
    if len(items) > 1:
        prev, nxt = items[idx - 1], items[(idx + 1) % len(items)]
        kb.append([_btn('◀ %d' % prev['n'], 'v', nid, prev['RequestID']),
                   _btn('📋 List', 'l', nid, idx // NOTICE_PAGE),
                   _btn('%d ▶' % nxt['n'], 'v', nid, nxt['RequestID'])])
    kb.append(link_row(nt.get('Url') or _app_url('Requests')))
    return _view('\n'.join(text), kb, note)


def notice_ask(items, action):
    """(text, keyboard) asking to confirm Accept all / Decline all."""
    nt, nid = items[0], items[0]['NoticeID']
    waiting = _waiting(items)
    if not waiting:
        return notice_list(items, 0, 'Nothing is waiting any more.')
    accept = action == 'a'
    text = ['%s all %d waiting transfers into %s?' % ('Accept' if accept else 'Decline', len(waiting), _where(nt)), '']
    text += [_line(it, icon=False) for it in waiting[:40]]
    if len(waiting) > 40:
        text.append('… and %d more' % (len(waiting) - 40))
    text += ['', 'Each one is applied from the date asked for (or today, if none).' if accept
             else 'Each one is closed as declined by %s.' % (nt.get('Dept') or 'your department')]
    kb = [[_btn(('✅ Yes, accept all %d' if accept else '❌ Yes, decline all %d') % len(waiting), 'all', action, nid)],
          [_btn('⬅ Back', 'l', nid, 0)]]
    return _view('\n'.join(text), kb)


def _resolve(uid, ids, action):
    """spChurchRegrpResolve as the presser. {RequestID (str): row}"""
    with connection.cursor() as cursor:
        cursor.execute(
            "EXEC spChurchRegrpResolve @ActorUID = %s, @IDs = %s, @Action = %s, @EffectiveDate = %s, @Note = %s",
            [uid, ','.join(str(i) for i in ids), action, None, 'Answered on Telegram'])
        rows = fetch_rows(cursor)
    out = {str(r.get('ID')): r for r in rows if r.get('ID') is not None}
    for i in ids:   # a refusal of the whole batch may come back without IDs
        out.setdefault(str(i), rows[0] if rows else {})
    return out


def _res_text(row):
    msg = row.get('Res') or ('Done' if row.get('Ok') else 'That could not be done.')
    return msg + (' ⚠️ ' + row['Warning'] if row.get('Warning') else '')


def _without_buttons(rows, request_id):
    """A keyboard (rows of button dicts) minus one request's crg:a / crg:d buttons."""
    mine = {'crg:a:%s' % request_id, 'crg:d:%s' % request_id}
    kept = [[b for b in row if b.get('callback_data') not in mine] for row in (rows or [])]
    return [row for row in kept if row]


def _label(rows, data):
    """'2' when the pressed button was 'Accept 2' in an old digest, else ''."""
    for row in rows or []:
        for b in row:
            if b.get('callback_data') == data:
                parts = (b.get('text') or '').split()
                return parts[-1] if parts and parts[-1].isdigit() else ''
    return ''


def _delete_after():
    """Seconds before the bot deletes a fully answered message; 0 keeps it."""
    value = getattr(settings, 'CHURCH_REGRP_DELETE_AFTER', None)
    if value in (None, ''):
        value = os.environ.get('CHURCH_REGRP_DELETE_AFTER')
    try:
        return max(0, int(value)) if value not in (None, '') else 120
    except ValueError:
        return 120


def _span(seconds):
    if seconds % 60 == 0:
        m = seconds // 60
        return '%d minute%s' % (m, '' if m == 1 else 's')
    return '%d seconds' % seconds


def telegram_press(uid, name, data, text='', keyboard=None):
    """One button press by member uid. Returns {Ok, Toast, Alert, Text, Keyboard, DeleteAfter}:
       Toast the pop-up; Text / Keyboard the message to show now (Text None: leave it);
       DeleteAfter the seconds after which the worker deletes the message (None: keep it)."""
    def out(ok, toast, view=None, alert=None, final=False):
        new_text = view[0] if view else None
        delay = _delete_after() if final and view else 0
        if delay:
            note = '\n\n🗑 Everything here is answered. This message will be deleted in %s.' % _span(delay)
            new_text = new_text[:4096 - len(note)] + note # type: ignore
        return {'Ok': bool(ok), 'Toast': (toast or '')[:190], 'Alert': (not ok) if alert is None else alert,
                'Text': new_text, 'Keyboard': view[1] if view else None, 'DeleteAfter': delay or None}

    p = data.split(':')

    # Messages from before notices: crg:a:<RequestID> / crg:d:<RequestID>.
    if len(p) == 3 and p[1] in ('a', 'd') and p[2].isdigit():
        accept = p[1] == 'a'
        row = _resolve(uid, [p[2]], 'Accept' if accept else 'Decline')[p[2]]
        msg = _res_text(row)
        if not row.get('Ok'):
            return out(False, msg)
        label = _label(keyboard, data)
        extra = '\n\n' + ('#%s ' % label if label else '') + '%s %s (%s)' % ('✅' if accept else '❌', msg, name)
        new_text = (text or '')[:max(0, 4096 - len(extra))] + extra
        kept = _without_buttons(keyboard, p[2])
        left = any(str(b.get('callback_data') or '').startswith('crg:') for row in kept for b in row)
        return out(True, msg, (new_text, kept), final=not left)

    kind = p[1] if len(p) > 1 else ''
    action, arg = None, ''
    try:
        if kind in ('l', 'v'):
            nid, arg = int(p[2]), (p[3] if len(p) > 3 else '0')
        elif kind in ('one', 'ask', 'all') and p[2] in ('a', 'd'):
            action, nid, arg = p[2], int(p[3]), (p[4] if len(p) > 4 else '')
        else:
            raise ValueError(data)
    except (IndexError, ValueError):
        return out(False, 'Unknown button.')

    items = notice_rows(nid, uid)
    if not items:
        return out(False, 'This list is no longer available. Please use the link.')
    if not items[0].get('Allowed'):
        return out(False, 'This list was sent to someone else.')

    done = not _waiting(items)
    if kind == 'l':
        return out(True, '', notice_list(items, int(arg) if arg.isdigit() else 0), final=done)
    if kind == 'v':
        # All answered (a number pressed on an older message): the list, without buttons.
        return out(True, '', notice_list(items) if done and len(items) > 1 else notice_item(items, arg), final=done)
    if kind == 'ask':
        return out(True, '', notice_ask(items, action), final=done)

    verb = 'Accept' if action == 'a' else 'Decline'
    icon = '✅' if action == 'a' else '❌'

    if kind == 'one':
        it = next((x for x in items if str(x['RequestID']) == arg), None)
        if it is None:
            return out(False, 'Unknown button.')
        if _state(it) != 'wait':
            view = notice_list(items) if done and len(items) > 1 else notice_item(items, arg)
            return out(False, 'Already answered: ' + _state_line(it), view, final=done)
        row = _resolve(uid, [arg], verb)[arg]
        ok, msg = bool(row.get('Ok')), _res_text(row)
        items = notice_rows(nid, uid)
        done = not _waiting(items)
        if len(items) == 1:
            return out(ok, msg, notice_item(items, arg), final=done)
        note = '%s %s: %s' % (icon if ok else '⚠️', it.get('Name'), msg)
        if not ok:
            return out(False, msg, notice_item(items, arg, note), final=done)
        # On to the next one still waiting (after this one, then from the top); none left: the list.
        idx = next((i for i, x in enumerate(items) if str(x['RequestID']) == arg), 0)
        nxt = next((x for x in items[idx + 1:] + items[:idx] if _state(x) == 'wait'), None)
        return out(True, msg, notice_item(items, nxt['RequestID'], note) if nxt else notice_list(items, 0, note),
                   final=nxt is None)

    # kind == 'all': every move still waiting, in one go.
    ids = [str(it['RequestID']) for it in _waiting(items)]
    if not ids:
        return out(False, 'Nothing is waiting any more.', notice_list(items, 0), final=True)
    res = _resolve(uid, ids, verb)
    done = [i for i in ids if res[i].get('Ok')]
    failed = [i for i in ids if i not in done]
    items = notice_rows(nid, uid)
    names = {str(it['RequestID']): it.get('Name') for it in items}
    lines = ['%s %s %d of %d.' % (icon, 'Accepted' if action == 'a' else 'Declined', len(done), len(ids))]
    lines += ['⚠️ %s: %s' % (names.get(i), _res_text(res[i])) for i in failed[:10]]
    lines += ['⚠️ %s: %s' % (names.get(i), res[i]['Warning']) for i in done if res[i].get('Warning')][:10]
    toast = lines[0] + (' %d could not be done.' % len(failed) if failed else '')
    return out(not failed, toast, notice_list(items, 0, '\n'.join(lines)), alert=bool(failed),
               final=not _waiting(items))


def _notice_sent(notice_id, message_id):
    with connection.cursor() as cursor:
        cursor.execute("EXEC spChurchRegrpNoticeSent @NoticeID = %s, @MessageID = %s", [notice_id, message_id])


def send_notices(did=None, everyone=False, all_waiting=False, url=None):
    """Claims the untold moves waiting for a department (did; None: every department), sends
       one notice per person to tell, and marks them. A department none of whose notices got
       through is left untold, for the digest. Returns {'Sent': n, 'Failed': n}.
       everyone: all in charge with a chat (the digest), else the first (a save).
       all_waiting: every waiting move, told or not (a reminder)."""
    with connection.cursor() as cursor:
        cursor.execute("EXEC spChurchRegrpNoticeClaim @DID = %s, @Everyone = %s, @All = %s, @Url = %s",
                       [did, 1 if everyone else 0, 1 if all_waiting else 0, url or _app_url('Requests')])
        claimed = fetch_rows(cursor)

    out = {'Sent': 0, 'Failed': 0}
    reached, tried = set(), {}
    for n in claimed:
        tried.setdefault(n['DID'], []).append(n['NoticeID'])
        sent = False
        try:
            items = notice_rows(n['NoticeID'], n['UID'])
            if items:
                text, kb = notice_item(items, items[0]['RequestID']) if len(items) == 1 else notice_list(items)
                sent = send_telegram(telegram_body(n['TelID'], text, kb))
        except Exception as e:
            print('Church Regrouping - notice failed:', e)
        if sent:
            out['Sent'] += 1
            reached.add(n['DID'])
            _notice_sent(n['NoticeID'], (sent.get('message_id') if isinstance(sent, dict) else None) or 0)
        else:
            out['Failed'] += 1
    for d, nids in tried.items():
        if d not in reached:
            for nid in nids:
                _notice_sent(nid, None)   # untold again
    return out


def notify_later(dids, url=None):
    """Sends the notices for these receiving departments on a background thread, so a slow
       Telegram never holds up (or fails) the save."""
    dids = sorted({int(d) for d in (dids or []) if str(d).strip().isdigit()})
    if not dids or not _bot_token():
        return

    def run():
        try:
            for did in dids:
                try:
                    send_notices(did=did, url=url)
                except Exception as e:
                    print('Church Regrouping - notices failed:', e)
        finally:
            close_old_connections()
            connection.close()

    threading.Thread(target=run, daemon=True).start()


# --- login ----------------------------------------------------------------------------

# Replaces GetMemberViewSet: the old one formatted the username and password
# straight into the EXEC, so a quote in either field was SQL injection.
# Accepts POST (what Code.js sends, so the password stays out of URLs and
# access logs) and GET (so anything still calling it the old way keeps working).
class ChurchRegrpGetMemberViewSet(APIView):
    def login(self, source):
        username = source.get('username') or ''
        password = source.get('password') or ''

        if not username or not password:
            return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpAppsScriptLogin @Username = %s, @Password = %s",
                    [username, password]
                )
                result = fetch_rows(cursor)

            if len(result) == 0:
                return Response({'error': 'Unauthorized Access'}, status=status.HTTP_401_UNAUTHORIZED)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)

    def get(self, request):
        return self.login(request.GET)

    def post(self, request):
        return self.login(request.data)


# --- reads ----------------------------------------------------------------------------

class ChurchRegrpGetContextViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        if not uid:
            return Response({'error': 'UID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetContext @UID = %s", [uid])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpGetGroupsViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        if not uid:
            return Response({'error': 'UID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetGroups @UID = %s", [uid])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpGetTasksViewSet(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetTasks")
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpGetTaskRefsViewSet(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetTaskRefs")
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpGetMembersViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        did = request.GET.get('DID', '')
        if not uid or not did.isdigit():
            return Response({'error': 'UID and DID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetMembers @UID = %s, @DID = %s", [uid, int(did)])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpGetRequestsViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        req_status = blank_to_none(request.GET.get('Status')) or 'Pending'
        days = request.GET.get('Days', '')

        if not uid:
            return Response({'error': 'UID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpGetRequests @UID = %s, @Status = %s, @Days = %s",
                    [uid, req_status, int(days) if days.isdigit() else None]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpSearchMembersViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        q = (request.GET.get('q') or '').strip()
        if not uid:
            return Response({'error': 'UID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpSearchMembers @UID = %s, @Q = %s", [uid, q[:50]])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# --- writes ---------------------------------------------------------------------------
#
# Each procedure answers with rows carrying Ok (1/0) and Res (a sentence), so
# a refusal such as "This member is not in one of your departments." arrives
# as a 200 with Ok = 0. Code.js turns Ok = 0 into an error for the page.

class ChurchRegrpSaveRequestViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        uid = data.get('UID')

        if not actor or not uid:
            return Response({'error': 'ActorUID and UID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        keep = data.get('KeepPrevious')

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpSaveRequest @ActorUID = %s, @UID = %s, @ToGID = %s, "
                    "@ToTaskCode = %s, @Notes = %s, @KeepPrevious = %s, @ToTID = %s, @ToPID = %s, "
                    "@EffectiveDate = %s",
                    [actor, uid,
                     blank_to_none(data.get('ToGID')),
                     blank_to_none(data.get('ToTaskCode')),
                     blank_to_none(data.get('Notes')),
                     None if keep is None else (1 if keep in (True, 1, '1', 'true') else 0),
                     blank_to_none(data.get('ToTID')),
                     blank_to_none(data.get('ToPID')),
                     blank_to_none(data.get('EffectiveDate'))]
                )
                result = fetch_rows(cursor)

            # A move into another department now waiting for it: the procedure fills
            # NotifyTelID / NotifyName / NotifyUID / NotifyMessage for the receiving
            # department's leader. NotifyUrl is the app link (sent by Apps Script).
            # The receiving department is told with a notice (see "Telegram notices"):
            # now, for a single save; for a save of many (NotifyLater), once all are
            # saved, when Code.js calls churchRegrpNotifyMoves/ — one message for them all.
            app_url = blank_to_none(data.get('AppUrl'))
            for row in result:
                if row.get('NotifyMessage'):
                    row['NotifyUrl'] = app_url
            if data.get('NotifyLater') not in (True, 1, '1', 'true'):
                notify_later([r.get('ToDID') for r in result if r.get('NotifyMessage')], app_url)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# After a save of many (Regroup -> Apply changes, each sent with NotifyLater): one
# notice per receiving department for every move it left waiting.
#     POST { "DIDs": [3, 7], "AppUrl": "<the app's link>" }
# Only moves nobody has been told about are sent, so a repeat sends nothing twice.
class ChurchRegrpNotifyMovesViewSet(APIView):
    def post(self, request):
        dids = request.data.get('DIDs') or []
        if isinstance(dids, (str, int)):
            dids = str(dids).split(',')
        notify_later(dids, blank_to_none(request.data.get('AppUrl')))
        return Response({'Ok': 1}, status=status.HTTP_200_OK)


class ChurchRegrpResolveViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        ids = data.get('IDs')
        action = data.get('Action')

        if not actor or not ids or action not in ('Apply', 'Reject', 'Cancel', 'Accept', 'Decline'):
            return Response({'error': 'ActorUID, IDs and a valid Action are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(ids, (list, tuple)):
            ids = ','.join(str(i) for i in ids)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpResolve @ActorUID = %s, @IDs = %s, @Action = %s, "
                    "@EffectiveDate = %s, @Note = %s",
                    [actor, str(ids), action,
                     blank_to_none(data.get('EffectiveDate')),
                     blank_to_none(data.get('Note'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpSetDeptLeaderViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        dept = data.get('Dept')

        if not actor or not dept:
            return Response({'error': 'ActorUID and Dept are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpSetDeptLeader @ActorUID = %s, @Dept = %s, @LeaderUID = %s, "
                    "@NF = %s, @EffectiveDate = %s",
                    [actor, dept,
                     blank_to_none(data.get('LeaderUID')),
                     1 if data.get('NF') in (True, 1, '1', 'true') else 0,
                     blank_to_none(data.get('EffectiveDate'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpMoveGroupViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        gid = data.get('GID')
        did = data.get('DID')

        if not actor or gid in (None, '') or did in (None, ''):
            return Response({'error': 'ActorUID, GID and DID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpMoveGroup @ActorUID = %s, @GID = %s, @DID = %s, @EffectiveDate = %s",
                    [actor, int(gid), int(did), blank_to_none(data.get('EffectiveDate'))]
                )
                result = fetch_rows(cursor)

            # One row per person in charge of the department the group left or joined
            # (its leader; with none, the subdivision's leader and assistants; with none,
            # the administrator), except whoever moved it: NotifyUID / NotifyName /
            # NotifyTelID / NotifyDID / NotifyMessage. NotifyUrl opens the Groups page on
            # NotifyDID (AppUrl is sent by Apps Script). NotifyTelegram is the sendMessage
            # body (None when they have no active TelegramID row). Sent from here.
            app_url = blank_to_none(data.get('AppUrl'))
            jobs = []
            for row in result:
                if row.get('NotifyMessage'):
                    row['NotifyUrl'] = with_param(app_url, 'dept', row.get('NotifyDID'))
                    row['NotifyTelegram'] = telegram_body(row.get('NotifyTelID'), row['NotifyMessage'],
                                                          [link_row(row['NotifyUrl'], '🔗 See the group')])
                    jobs.append((row['NotifyTelegram'], None))
            send_later(jobs)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpGroupHistoryViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        gid = request.GET.get('GID', '')
        if not uid or not gid.isdigit():
            return Response({'error': 'UID and GID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetGroupHistory @UID = %s, @GID = %s", [uid, int(gid)])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpArchiveViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        kind = data.get('Kind')
        ref_id = data.get('RefID')

        if not actor or kind not in ('Group', 'Dept') or ref_id in (None, ''):
            return Response({'error': 'ActorUID, Kind and RefID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpArchive @ActorUID = %s, @Kind = %s, @RefID = %s, @Archive = %s, @Reason = %s",
                    [actor, kind, int(ref_id),
                     1 if data.get('Archive') in (True, 1, '1', 'true') else 0,
                     blank_to_none(data.get('Reason'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpSetGroupRuleViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        gid = data.get('GID')

        if not actor or gid in (None, ''):
            return Response({'error': 'ActorUID and GID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpSetGroupRule @ActorUID = %s, @GID = %s, @NoGYJN = %s",
                    [actor, int(gid), 1 if data.get('NoGYJN') in (True, 1, '1', 'true') else 0]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpSetMemberProfileViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        uid = data.get('UID')

        if not actor or not uid:
            return Response({'error': 'ActorUID and UID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                # Gender is written to Registration by its own procedure; the rest is the profile.
                if 'Gender' in data:
                    cursor.execute(
                        "EXEC spChurchRegrpSetMemberGender @ActorUID = %s, @UID = %s, @Gender = %s",
                        [actor, uid, blank_to_none(data.get('Gender'))]
                    )
                else:
                    cursor.execute(
                        "EXEC spChurchRegrpSetMemberProfile @ActorUID = %s, @UID = %s, @Category = %s, @Schedule = %s",
                        [actor, uid, blank_to_none(data.get('Category')), blank_to_none(data.get('Schedule'))]
                    )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpProfileHistoryViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        member = request.GET.get('MemberUID')
        if not uid or not member:
            return Response({'error': 'UID and MemberUID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetProfileHistory @UID = %s, @MemberUID = %s", [uid, member])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# --- MCT internal groups (IT admin / CT leadership only; the procedures check) ------------

class ChurchRegrpCTGetMembersViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        if not uid:
            return Response({'error': 'UID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpCTGetMembers @UID = %s", [uid])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpCTGetGroupsViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        if not uid:
            return Response({'error': 'UID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpCTGetGroups @UID = %s", [uid])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpCTMoveViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        uids = data.get('UIDs')

        if not actor or not uids:
            return Response({'error': 'ActorUID and UIDs are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(uids, (list, tuple)):
            uids = ','.join(str(u) for u in uids)

        ct_gid = blank_to_none(data.get('CTGID'))

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpCTMove @ActorUID = %s, @UIDs = %s, @CTGID = %s, @EffectiveDate = %s",
                    [actor, str(uids), None if ct_gid is None else int(ct_gid),
                     blank_to_none(data.get('EffectiveDate'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpCTSetLeaderViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        uids = data.get('UIDs')

        if not actor or not uids:
            return Response({'error': 'ActorUID and UIDs are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(uids, (list, tuple)):
            uids = ','.join(str(u) for u in uids)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpCTSetLeader @ActorUID = %s, @UIDs = %s, @IsLeader = %s, @EffectiveDate = %s",
                    [actor, str(uids),
                     1 if data.get('IsLeader') in (True, 1, '1', 'true') else 0,
                     blank_to_none(data.get('EffectiveDate'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpCTHistoryViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        member = request.GET.get('MemberUID')
        if not uid or not member:
            return Response({'error': 'UID and MemberUID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpCTHistory @UID = %s, @MemberUID = %s", [uid, member])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpCTSaveGroupViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        name = (data.get('Grp') or '').strip()

        if not actor or not name:
            return Response({'error': 'ActorUID and Grp are required.'}, status=status.HTTP_400_BAD_REQUEST)

        gid = blank_to_none(data.get('GID'))
        active = data.get('AccountActive')

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpCTSaveGroup @ActorUID = %s, @GID = %s, @Grp = %s, @AccountActive = %s",
                    [actor, None if gid is None else int(gid), name[:50],
                     None if active is None else (1 if active in (True, 1, '1', 'true') else 0)]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# --- subdivisions (admin) -----------------------------------------------------------------

class ChurchRegrpGetSubdivisionsViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        if not uid:
            return Response({'error': 'UID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetSubdivisions @UID = %s", [uid])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


class ChurchRegrpSetSubdivLeaderViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        sid = data.get('SID')

        if not actor or sid in (None, ''):
            return Response({'error': 'ActorUID and SID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpSetSubdivLeader @ActorUID = %s, @SID = %s, @LeaderUID = %s, @EffectiveDate = %s",
                    [actor, int(sid), blank_to_none(data.get('LeaderUID')), blank_to_none(data.get('EffectiveDate'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# A subdivision's Leader or an Assistant: add (End = 0) or end (End = 1).
class ChurchRegrpSetSubdivRoleViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        sid = data.get('SID')
        role = data.get('Role')

        if not actor or sid in (None, '') or role not in ('Leader', 'Assistant'):
            return Response({'error': 'ActorUID, SID and Role (Leader / Assistant) are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpSetSubdivRole @ActorUID = %s, @SID = %s, @Role = %s, @UID = %s, "
                    "@End = %s, @EffectiveDate = %s",
                    [actor, int(sid), role, blank_to_none(data.get('UID')),
                     1 if data.get('End') in (True, 1, '1', 'true') else 0,
                     blank_to_none(data.get('EffectiveDate'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# The feedback leader of a category (FeedbackInfo).
class ChurchRegrpSetFeedbackLeaderViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')

        if not actor or not data.get('Category') or not data.get('UID'):
            return Response({'error': 'ActorUID, Category and UID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpSetFeedbackLeader @ActorUID = %s, @Category = %s, @UID = %s",
                    [actor, str(data.get('Category')), str(data.get('UID'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# Departments' feedback category (DeptCategoryLog, and the groups' copy). DIDs: '8,9,10';
# Category blank ends it; EffectiveDate today or earlier.
class ChurchRegrpSetDeptCategoryViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        dids = data.get('DIDs')

        if isinstance(dids, (list, tuple)):
            dids = ','.join(str(d) for d in dids)
        if not actor or not dids:
            return Response({'error': 'ActorUID and DIDs are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpSetDeptCategory @ActorUID = %s, @DIDs = %s, @Category = %s, @EffectiveDate = %s",
                    [actor, str(dids), blank_to_none(data.get('Category')), blank_to_none(data.get('EffectiveDate'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# Corrects the start / end dates of one dated row. LogName: DeptLeader | GroupDept | SubdivRole | DeptCategory.
class ChurchRegrpEditDatesViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        log = data.get('LogName')
        row_id = data.get('ID')

        if not actor or log not in ('DeptLeader', 'GroupDept', 'SubdivRole', 'DeptCategory') or row_id in (None, ''):
            return Response({'error': 'ActorUID, LogName and ID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpEditDates @ActorUID = %s, @LogName = %s, @ID = %s, @StartDate = %s, @EndDate = %s",
                    [actor, log, int(row_id), blank_to_none(data.get('StartDate')), blank_to_none(data.get('EndDate'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# The dated rows of a department, group or subdivision. Kind: Dept | Group | Subdiv.
class ChurchRegrpGetHistoryViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        kind = request.GET.get('Kind')
        ref = request.GET.get('RefID') or ''

        if not uid or kind not in ('Dept', 'Group', 'Subdiv') or not ref.isdigit():
            return Response({'error': 'UID, Kind and RefID are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpGetHistory @UID = %s, @Kind = %s, @RefID = %s", [uid, kind, int(ref)])
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# NO LONGER USED — the app sets categories per department (churchRegrpSetDeptCategory/).
# Kept only so an existing urls.py entry for churchRegrpSetGroupCategory/ still imports;
# remove the route and this class together when convenient. Its procedure is no longer created.
class ChurchRegrpSetGroupCategoryViewSet(APIView):
    def post(self, request):
        data = request.data
        actor = data.get('ActorUID')
        gids = data.get('GIDs')

        if isinstance(gids, (list, tuple)):
            gids = ','.join(str(g) for g in gids)
        if not actor or not gids:
            return Response({'error': 'ActorUID and GIDs are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "EXEC spChurchRegrpSetGroupCategory @ActorUID = %s, @GIDs = %s, @Category = %s",
                    [actor, str(gids), blank_to_none(data.get('Category'))]
                )
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# --- member sheet sync ---------------------------------------------------------------------
#
# Returns every member's row for the Google Sheet — INCLUDING usernames and
# passwords — so it answers only a request carrying the shared sync key:
#
#     settings.py (or the environment):  CHURCH_REGRP_SYNC_KEY = '<long random string>'
#     Apps Script script property:       SYNC_KEY = the same string
#
# With no key configured it refuses everything rather than serving openly.

import hmac


def sync_key_ok(request):
    expected = getattr(settings, 'CHURCH_REGRP_SYNC_KEY', None) or os.environ.get('CHURCH_REGRP_SYNC_KEY')
    given = request.headers.get('X-Sync-Key') or ''
    return bool(expected) and hmac.compare_digest(str(expected), str(given))


class ChurchRegrpMemberSheetViewSet(APIView):
    def get(self, request):
        if not sync_key_ok(request):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpMemberSheet")
                result = fetch_rows(cursor)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# --- transfer digest (Telegram) -------------------------------------------------------
#
# One message per receiving department leader listing the moves into their
# department that wait for them to accept and that they have not been told
# about yet, each with its own Accept / Decline buttons. Saving a move already
# sends its own message (and marks it), so the digest picks up what that missed
# (a leader with no Telegram then, a failed send) and, with All, reminders.
#
# send_transfer_digests() sends them all and marks what was delivered. Run it on
# a schedule (Heroku Scheduler, cron, or the worker's job queue), e.g.
#     POST churchRegrpTransferDigest/  {"Send": true}        (X-Sync-Key)
# Or by hand:
#
#     for msg in transfer_digests():
#         if send_telegram(msg['telegram']):
#             mark_transfers_sent(msg['request_ids'])        # so they are not sent again
#
# msg['telegram'] is the Telegram Bot API sendMessage body, ready to pass:
#     { 'chat_id': ..., 'text': ..., 'reply_markup': {'inline_keyboard': [[{'text', 'url'}]]} }
# (with python-telegram-bot: bot.send_message(chat_id=..., text=..., reply_markup=
#  InlineKeyboardMarkup.de_json(msg['telegram']['reply_markup'], bot)), or POST it as JSON to
#  https://api.telegram.org/bot<token>/sendMessage).
#
# The button opens the app's Changes page:
#     settings.py (or the environment):  CHURCH_REGRP_APP_URL = 'https://script.google.com/macros/s/<id>/exec'
#
# A leader with no active TelegramID row comes back with 'telegram': None —
# nothing to send; their transfers stay unmarked and are listed again next time.
#
# Or over HTTP, with the X-Sync-Key header (as the member sheet):
#     GET  churchRegrpTransferDigest/            the messages   (?all=1: every waiting transfer, a reminder)
#     POST churchRegrpTransferDigest/            body { "RequestIDs": "12,15,19" } -> marks them sent


def _app_url(page='Requests'):
    base = getattr(settings, 'CHURCH_REGRP_APP_URL', None) or os.environ.get('CHURCH_REGRP_APP_URL') or ''
    if not base.startswith('https://'):
        return None
    return base + ('&' if '?' in base else '?') + 'page=' + page


def transfer_digests(all_waiting=False):
    """One dict per person in charge of a receiving department (its leader; with none, the
       subdivision's leader and assistants; with none, the administrator) — a department can
       give more than one. Marking any one's request_ids marks the department's transfers:
       { dept, leader_uid, leader_name, tel_id, moves, request_ids, message, url, telegram }"""
    with connection.cursor() as cursor:
        cursor.execute("EXEC spChurchRegrpTransferDigest @All = %s", [1 if all_waiting else 0])
        rows = fetch_rows(cursor)

    url = _app_url('Requests')
    out = []
    for r in rows:
        # A row of Accept / Decline per move, numbered as in the message.
        ids = [i for i in str(r.get('RequestIDs') or '').split(',') if i]
        keyboard = [link_row(url)] + [answer_row(rid, ' %d' % n) for n, rid in enumerate(ids, 1)]
        telegram = telegram_body(r.get('TelID'), r.get('Message'), keyboard)
        out.append({
            'dept':        r.get('Dept'),
            'leader_uid':  r.get('LeaderUID'),
            'leader_name': r.get('LeaderName'),
            'in_charge_as': r.get('InChargeAs'),   # 'Department leader' | 'Subdivision' | 'Administrator'
            'tel_id':      r.get('TelID'),
            'moves':       r.get('Moves'),
            'request_ids': r.get('RequestIDs'),
            'message':     r.get('Message'),
            'url':         url,
            'telegram':    telegram,
        })
    return out


def send_transfer_digests(all_waiting=False):
    """Sends the digest as notices (one per person in charge of each receiving department,
       with the list and its buttons) and marks what was delivered. all_waiting: a reminder
       of every waiting move, told or not. Returns {'Sent': n, 'Failed': n}.
       Departments where nobody in charge has a Telegram chat are skipped (and stay untold)."""
    return send_notices(everyone=True, all_waiting=all_waiting)


def mark_transfers_sent(request_ids):
    """request_ids: '12,15,19' (a digest's request_ids). Returns how many were marked."""
    if isinstance(request_ids, (list, tuple)):
        request_ids = ','.join(str(i) for i in request_ids)
    with connection.cursor() as cursor:
        cursor.execute("EXEC spChurchRegrpTransferMarkSent @IDs = %s", [str(request_ids or '')])
        rows = fetch_rows(cursor)
    return (rows[0].get('Marked') if rows else 0) or 0


class ChurchRegrpTransferDigestViewSet(APIView):
    def get(self, request):
        if not sync_key_ok(request):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        try:
            return Response(transfer_digests(request.GET.get('all') == '1'), status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)

    def post(self, request):
        if not sync_key_ok(request):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        try:
            # {"Send": true} sends every digest (and marks them); add "All": true for a reminder of all.
            if request.data.get('Send') in (True, 1, '1', 'true'):
                return Response(send_transfer_digests(request.data.get('All') in (True, 1, '1', 'true')),
                                status=status.HTTP_200_OK)
            return Response({'Marked': mark_transfers_sent(request.data.get('RequestIDs'))}, status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)


# --- Telegram button presses (from the bot worker) ------------------------------------------
#
# The worker posts each press here (X-Sync-Key):
#     { "TelegramUserID": <callback_query.from.id>, "Data": "<callback_data>",
#       "Text": "<the message's text>", "Keyboard": [[{button}, ...], ...] }
# and gets back { Ok, Toast, Alert, Text, Keyboard }: the pop-up, and the message to show
# now (Text null: leave it as it is). See "Telegram notices" for the callback_data.
# The member is whoever that Telegram account belongs to (TelegramID, active), and
# spChurchRegrpResolve decides as it does for the site: only someone in charge of the
# receiving department can answer. Accept applies the move from the date asked for.
#
# The first worker version's body { TelegramUserID, RequestID, Action } is still answered
# with { Ok, Applied, Message, By }.

class ChurchRegrpTelegramAnswerViewSet(APIView):
    def post(self, request):
        if not sync_key_ok(request):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        tel = str(data.get('TelegramUserID') or '').strip()
        press = str(data.get('Data') or '').strip()
        rid = str(data.get('RequestID') or '').strip()
        action = data.get('Action')
        if not tel or not (press.startswith('crg:') or (rid.isdigit() and action in ('Accept', 'Decline'))):
            return Response({'error': 'TelegramUserID and Data (or RequestID and Action) are required.'},
                            status=status.HTTP_400_BAD_REQUEST)

        def refuse(message):
            if press:
                return Response({'Ok': False, 'Toast': message, 'Alert': True, 'Text': None, 'Keyboard': None},
                                status=status.HTTP_200_OK)
            return Response({'Ok': False, 'Applied': False, 'Message': message, 'By': None}, status=status.HTTP_200_OK)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spChurchRegrpTelegramUser @TelID = %s", [tel])
                users = fetch_rows(cursor)

            if not users:
                return refuse("This Telegram account isn't linked to anyone with access to Church Regrouping.")
            if len({u['UID'] for u in users}) > 1:
                return refuse('This Telegram account is linked to more than one member. Please answer on the site.')
            uid, name = users[0]['UID'], users[0].get('Name')

            if press:
                keyboard = data.get('Keyboard')
                return Response(telegram_press(uid, name, press, data.get('Text') or '',
                                               keyboard if isinstance(keyboard, list) else []),
                                status=status.HTTP_200_OK)

            row = _resolve(uid, [rid], action)[rid]
            ok = bool(row.get('Ok'))
            return Response({'Ok': ok, 'Applied': bool(row.get('Applied')), 'Message': _res_text(row), 'By': name},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return error_response(e)
