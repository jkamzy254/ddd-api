"""
CT Attendance — class reports in Telegram, for the bot worker (Heroku).

Two commands and the buttons on the messages they lead to:

    /ctreport   in a private chat: the running sessions you may see (every one
                for admins and CT Leadership), then a session's report, with
                ◀ ▶ through its classes, 📅 a list of them, and 📤 post to its group
    /ctgroup    in a group the bot is in: choose which sessions post their
                reports to this group

All the logic is on the Django server (ct_class_report.py). This file passes
each command and button press to ctTelegramAnswer/, which acts as the member
linked to that Telegram account, and shows what it answers. New buttons need
no change here.

Worker config vars (heroku config:set ...). Each falls back to Church
Regrouping's, so on the same server nothing new is needed:
    APPS_SCRIPT_API_URL   the Django base, e.g. https://<server>/api/   (-> APPS_SCRIPT_API_URL)
    APPS_SCRIPT_SYNC_KEY  the same value as on the Django server       (-> APPS_SCRIPT_SYNC_KEY)

Copy this file next to the bot and register both handlers (python-telegram-bot v20+),
beside the Church Regrouping one:

    from telegram.ext import CallbackQueryHandler, CommandHandler
    from .responses.ct_report_handler import ptb_ct_report_button, ptb_ct_report_command
    application.add_handler(CommandHandler(['ctreport', 'ctgroup'], ptb_ct_report_command))
    application.add_handler(CallbackQueryHandler(ptb_ct_report_button, pattern=r'^ctr:'))

Optionally list them in BotFather (/setcommands) so they show in the menu:
    ctreport - Class reports of your CT sessions
    ctgroup - Choose which sessions post their reports to this group

In a group, a bot with privacy mode on still receives commands, so /ctgroup
works without changing that. Only button data starting 'ctr:' is ours.
No extra packages: only the standard library is used here.
"""

import asyncio
import json
import os
import urllib.error
import urllib.request

PREFIX = 'ctr:'


def _env(*names):
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return ''


def _api(path, body):
    base = os.environ.get('APPS_SCRIPT_API_URL', '').rstrip('/') + '/'
    req = urllib.request.Request(
        base + path,
        data=json.dumps(body).encode('utf-8'),
        headers={'Content-Type': 'application/json',
                 'X-Sync-Key': os.environ.get('APPS_SCRIPT_SYNC_KEY', '')})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return json.loads(res.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return {'error': 'The server refused the bot (sync key mismatch).'}
        if e.code == 404:
            return {'error': 'The server has no ctTelegramAnswer/ route yet.'}
        try:
            res = json.loads(e.read().decode('utf-8'))
        except ValueError:
            res = None
        if isinstance(res, dict) and res.get('error'):
            return res
        return {'error': 'CT Attendance could not handle this (HTTP %s). Please use the app.' % e.code}


def ask(body):
    """Posts one press or command. Never raises; a failure comes back as an error answer."""
    try:
        res = _api('ctTelegramAnswer/', body)
    except Exception as e:
        print('CT Attendance - request failed:', e)
        res = {'error': 'Could not reach CT Attendance. Please try again, or use the app.'}
    if not isinstance(res, dict) or res.get('error'):
        message = str((res or {}).get('error') or 'Something went wrong.')
        return {'Ok': False, 'Toast': message[:190], 'Alert': True, 'Text': None, 'Keyboard': None,
                'Error': message}
    return res


def _chat(chat):
    return {'ChatID': chat.id if chat else None,
            'ChatType': chat.type if chat else 'private',
            'ChatTitle': getattr(chat, 'title', None) if chat else None}


def _markup(kb, bot):
    from telegram import InlineKeyboardMarkup
    return InlineKeyboardMarkup.de_json({'inline_keyboard': kb}, bot) if kb else None


# --- python-telegram-bot (v20+) -------------------------------------------------------

async def ptb_ct_report_command(update, context):
    """/ctreport and /ctgroup: the server's answer, as a reply."""
    msg = update.effective_message
    if msg is None or update.effective_user is None:
        return
    command = (msg.text or '').split()[0].lstrip('/').split('@')[0].lower() if msg.text else ''

    res = await asyncio.to_thread(ask, dict(_chat(update.effective_chat),
                                            TelegramUserID=update.effective_user.id, Command=command))
    text = res.get('Text') or res.get('Error')
    if not text:
        return
    try:
        await msg.reply_text(text[:4096], reply_markup=_markup(res.get('Keyboard') or [], context.bot))
    except Exception as e:
        print('CT Attendance - reply failed:', e)


async def ptb_ct_report_button(update, context):
    query = update.callback_query
    data = query.data or ''
    if not data.startswith(PREFIX):
        return

    # A deleted or too-old message arrives as InaccessibleMessage (nothing to edit).
    msg = query.message
    usable = msg is not None and getattr(msg, 'is_accessible', True)

    res = await asyncio.to_thread(ask, dict(_chat(msg.chat if msg is not None else None),
                                            TelegramUserID=query.from_user.id, Data=data))

    try:
        await query.answer((res.get('Toast') or '')[:190] or None, show_alert=bool(res.get('Alert')))
    except Exception as e:
        print('CT Attendance - answer failed:', e)

    if not usable:
        return
    kb = res.get('Keyboard') or []
    try:
        if res.get('Text') is not None:
            await query.edit_message_text(res['Text'][:4096], reply_markup=_markup(kb, context.bot))
        elif res.get('KeyboardOnly'):
            await query.edit_message_reply_markup(reply_markup=_markup(kb, context.bot))
    except Exception as e:
        # "Message is not modified" (Refresh with nothing new) is harmless.
        if 'not modified' not in str(e).lower():
            print('CT Attendance - edit failed:', e)
