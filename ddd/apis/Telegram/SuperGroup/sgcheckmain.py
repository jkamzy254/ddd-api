import textwrap
from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

import logging

from telegram import ForceReply, Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ChatMemberHandler, ContextTypes
from telegram.helpers import escape_markdown
from telegram.constants import ParseMode


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def escape_markdown_v2(text):
    return escape_markdown(text, version=2)

sgyes_msg = textwrap.dedent(f"""
    🔧 *GROUP CHAT STATUS* 🌐

    ✅ This group chat *is* a SuperGroup 🙂

    _{escape_markdown_v2("Fighting everyone!")}_ 
    """)

sgno_msg = textwrap.dedent(f"""
    🔧 *GROUP CHAT STATUS* 🌐

    ⚠️ This group chat *IS NOT A* a SuperGroup‼️ 
    
    You can make this group chat into a SuperGroup 
    {escape_markdown_v2("1. Adding new admin (If there is no admin other than the owner)")}
    {escape_markdown_v2("2. Allowing the admin to add new admins")}
    This will turn your group chat into a SuperGroup
    
    _{escape_markdown_v2("Please type '/check' on the chat to check again after following the step")}s_ 
    """)

async def bot_added_to_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    member = update.my_chat_member 

    # Check if the bot was added (status changes from 'kicked' to 'member' or 'administrator')
    if member.new_chat_member.user.id == context.bot.id:
        if chat.type == "supergroup":
            await context.bot.send_message(chat_id=chat.id, text=sgyes_msg, parse_mode=ParseMode.MARKDOWN_V2)
            await context.bot.leave_chat(chat.id)
        else:
            await context.bot.send_message(chat_id=chat.id, text=sgno_msg, parse_mode=ParseMode.MARKDOWN_V2)

        # Leave after sending the message
async def check_group_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat

    if chat.type == "supergroup":
        await context.bot.send_message(chat_id=chat.id, text=sgyes_msg, parse_mode=ParseMode.MARKDOWN_V2)
        await context.bot.leave_chat(chat.id)
    else:
        await context.bot.send_message(chat_id=chat.id, text=sgno_msg, parse_mode=ParseMode.MARKDOWN_V2)

def main():
    token = os.environ.get('SG_BOT_TOKEN')
    application = Application.builder().token(token).build()

    application.add_handler(ChatMemberHandler(bot_added_to_chat, chat_member_types=ChatMemberHandler.MY_CHAT_MEMBER))
    application.add_handler(CommandHandler('check', check_group_type))

    application.run_polling()

    # return application