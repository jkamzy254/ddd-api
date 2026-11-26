"""
Church Regrouping — Accept / Decline buttons, for the Telegram bot worker (Heroku).

The Django server sends the messages. Their Accept / Decline buttons are
callback buttons, so Telegram delivers each press to this worker (whoever
receives the bot's updates). This file answers them: it posts the press to the
Django server, which acts as the member linked to that Telegram account, then
updates the message in the chat.

Worker config vars (heroku config:set ...):
    CHURCH_REGRP_API_URL   the Django base the routes hang off, e.g. https://<server>/api/
                           (the same base Apps Script uses: its API_URL script property)
    CHURCH_REGRP_SYNC_KEY  the same value as CHURCH_REGRP_SYNC_KEY on the Django server

Copy this file next to the bot and register the handler (python-telegram-bot v20+):

    from telegram.ext import CallbackQueryHandler
    from .responses.regrouping_handler import ptb_church_regrp_button
    application.add_handler(CallbackQueryHandler(ptb_church_regrp_button, pattern=r'^crg:'))

Only button data starting 'crg:' is ours ('crg:a:<RequestID>' accept,
'crg:d:<RequestID>' decline); leave every other callback to the bot's own
handlers. No extra packages: only the standard library is used here.
"""

import asyncio
import json
import os
import urllib.error
import urllib.request

PREFIX = 'crg:'


def _api(path, body):
    base = os.environ.get('CHURCH_REGRP_API_URL', '').rstrip('/') + '/'
    req = urllib.request.Request(
        base + path,
        data=json.dumps(body).encode('utf-8'),
        headers={'Content-Type': 'application/json',
                 'X-Sync-Key': os.environ.get('CHURCH_REGRP_SYNC_KEY', '')})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            return json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        # Django answers refusals and failures with a 403/500 status and {"error": ...};
        # pass that on instead of treating it as "could not reach".
        if e.code == 403:
            return {'error': 'The server refused the bot (sync key mismatch).'}
        try:
            res = json.loads(e.read().decode('utf-8'))
        except ValueError:
            res = None
        if isinstance(res, dict) and (res.get('error') or res.get('Message')):
            return res
        return {'error': 'Church Regrouping could not handle this (HTTP %s). Please use the link.' % e.code}


def answer_press(telegram_user_id, data):
    """Sends one press to the server. Returns (ok, toast, line):
         toast  the short pop-up the presser sees
         line   what to add to the message ('' when nothing changed)"""
    try:
        _, code, request_id = data.split(':', 2)
        action = {'a': 'Accept', 'd': 'Decline'}[code]
    except (ValueError, KeyError):
        return False, 'Unknown button.', ''

    try:
        res = _api('churchRegrpTelegramAnswer/',
                   {'TelegramUserID': telegram_user_id, 'RequestID': request_id, 'Action': action})
    except Exception as e:
        print('Church Regrouping - answer failed:', e)
        return False, 'Could not reach Church Regrouping. Please try again, or use the link.', ''

    if res.get('error'):
        return False, str(res['error'])[:190], ''

    ok, msg = bool(res.get('Ok')), res.get('Message') or ''
    if not ok:
        # e.g. "Not waiting for you to accept it." -- someone already answered it.
        return False, msg[:190], ''
    icon = '✅' if action == 'Accept' else '❌'
    by = res.get('By')
    return True, msg[:190], '%s %s%s' % (icon, msg, ' (%s)' % by if by else '')


def _without_buttons(rows, request_id):
    """The keyboard (list of rows of button dicts) minus this request's buttons."""
    mine = {'%sa:%s' % (PREFIX, request_id), '%sd:%s' % (PREFIX, request_id)}
    kept = [[b for b in row if b.get('callback_data') not in mine] for row in rows]
    return [row for row in kept if row]


def _label(rows, data):
    """' 2' when the pressed button was 'Accept 2' in a digest, else ''."""
    for row in rows:
        for b in row:
            if b.get('callback_data') == data:
                parts = b.get('text', '').split()
                return ' ' + parts[-1] if parts and parts[-1].isdigit() else ''
    return ''


# --- python-telegram-bot (v20+) -------------------------------------------------------

async def ptb_church_regrp_button(update, context):
    from telegram import InlineKeyboardMarkup

    query = update.callback_query
    data = query.data or ''
    if not data.startswith(PREFIX):
        return

    ok, toast, line = await asyncio.to_thread(answer_press, query.from_user.id, data)
    await query.answer(toast, show_alert=not ok)
    # A deleted or too-old message arrives as InaccessibleMessage (no text/buttons to edit).
    if not ok or not query.message or not getattr(query.message, 'is_accessible', True):
        return

    request_id = data.split(':', 2)[2]
    markup = query.message.reply_markup
    rows = [[b.to_dict() for b in row] for row in markup.inline_keyboard] if markup else []
    label = _label(rows, data)
    extra = '\n\n' + (('#' + label.strip() + ' ') if label else '') + line
    text = (query.message.text or '')[:max(0, 4096 - len(extra))] + extra   # trim the old text, never the new line
    kept = _without_buttons(rows, request_id)
    try:
        await query.edit_message_text(text[:4096], disable_web_page_preview=True,
                                      reply_markup=InlineKeyboardMarkup.de_json({'inline_keyboard': kept}, context.bot) if kept else None)
    except Exception as e:
        print('Church Regrouping - edit failed:', e)
