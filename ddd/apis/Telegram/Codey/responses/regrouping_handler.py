"""
Church Regrouping — Telegram button presses, for the bot worker (Heroku).

The Django server sends the messages. Their buttons are callback buttons, so
Telegram delivers each press to this worker (whoever receives the bot's
updates). This file passes the press on to the Django server
(churchRegrpTelegramAnswer/), which acts as the member linked to that Telegram
account and answers with what to show: a pop-up, and the message's new text and
buttons (the list of moves, one move in full, "Accept all?", ...). All the
logic is on the server; this only relays, so new buttons need no change here.

When everything in a message is answered, the server's answer carries
DeleteAfter (seconds, 120 by default): this worker then deletes the message.
A restart of the worker inside that time forgets the deletion, and Telegram
lets a bot delete its message only in the first 48 hours.

Worker config vars (heroku config:set ...):
    CHURCH_REGRP_API_URL   the Django base the routes hang off, e.g. https://<server>/api/
                           (the same base Apps Script uses: its API_URL script property)
    CHURCH_REGRP_SYNC_KEY  the same value as CHURCH_REGRP_SYNC_KEY on the Django server

Copy this file next to the bot and register the handler (python-telegram-bot v20+):

    from telegram.ext import CallbackQueryHandler
    from .responses.regrouping_handler import ptb_church_regrp_button
    application.add_handler(CallbackQueryHandler(ptb_church_regrp_button, pattern=r'^crg:'))

Only button data starting 'crg:' is ours; leave every other callback to the
bot's own handlers. No extra packages: only the standard library is used here.
"""

import asyncio
import json
import os
import urllib.error
import urllib.request

PREFIX = 'crg:'

_deleting = set()   # (chat_id, message_id) already waiting to be deleted
_tasks = set()      # keeps the delete tasks alive until they finish


def _api(path, body):
    base = os.environ.get('CHURCH_REGRP_API_URL', '').rstrip('/') + '/'
    req = urllib.request.Request(
        base + path,
        data=json.dumps(body).encode('utf-8'),
        headers={'Content-Type': 'application/json',
                 'X-Sync-Key': os.environ.get('CHURCH_REGRP_SYNC_KEY', '')})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
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
        if isinstance(res, dict) and res.get('error'):
            return res
        return {'error': 'Church Regrouping could not handle this (HTTP %s). Please use the link.' % e.code}


def press(body):
    """Posts one press. Returns {Ok, Toast, Alert, Text, Keyboard} (Text None: leave the message)."""
    try:
        res = _api('churchRegrpTelegramAnswer/', body)
    except Exception as e:
        print('Church Regrouping - press failed:', e)
        res = {'error': 'Could not reach Church Regrouping. Please try again, or use the link.'}
    if not isinstance(res, dict) or res.get('error'):
        return {'Ok': False, 'Toast': str((res or {}).get('error') or 'Something went wrong.')[:190],
                'Alert': True, 'Text': None, 'Keyboard': None}
    return res


# --- python-telegram-bot (v20+) -------------------------------------------------------

async def _delete_later(bot, chat_id, message_id, delay):
    try:
        await asyncio.sleep(delay)
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        # Already deleted by the user, or older than 48 hours.
        print('Church Regrouping - delete failed:', e)
    finally:
        _deleting.discard((chat_id, message_id))


def _schedule_delete(bot, msg, delay):
    key = (msg.chat_id, msg.message_id)
    if key in _deleting:
        return
    _deleting.add(key)
    task = asyncio.create_task(_delete_later(bot, key[0], key[1], delay))
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)


async def ptb_church_regrp_button(update, context):
    from telegram import InlineKeyboardMarkup

    query = update.callback_query
    data = query.data or ''
    if not data.startswith(PREFIX):
        return

    # A deleted or too-old message arrives as InaccessibleMessage (no text/buttons to edit).
    msg = query.message
    usable = msg is not None and getattr(msg, 'is_accessible', True)
    assert msg is not None
    markup = msg.reply_markup if usable else None

    res = await asyncio.to_thread(press, {
        'TelegramUserID': query.from_user.id,
        'Data': data,
        'Text': (msg.text or '') if usable else '',
        'Keyboard': [[b.to_dict() for b in row] for row in markup.inline_keyboard] if markup else [],
    })

    try:
        await query.answer(res.get('Toast') or None, show_alert=bool(res.get('Alert')))
    except Exception as e:
        print('Church Regrouping - answer failed:', e)

    if not usable:
        return
    try:
        delay = int(res.get('DeleteAfter') or 0)
    except (TypeError, ValueError):
        delay = 0
    if delay > 0:
        _schedule_delete(context.bot, msg, delay)
    if res.get('Text') is None:
        return
    kb = res.get('Keyboard') or []
    try:
        await query.edit_message_text(
            res['Text'][:4096],
            reply_markup=InlineKeyboardMarkup.de_json({'inline_keyboard': kb}, context.bot) if kb else None)
    except Exception as e:
        # "Message is not modified" (e.g. the page button pressed on the same page) is harmless.
        if 'not modified' not in str(e).lower():
            print('Church Regrouping - edit failed:', e)
