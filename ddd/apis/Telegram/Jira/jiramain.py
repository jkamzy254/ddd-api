from dotenv import load_dotenv, find_dotenv
import os
from django.db import connection
load_dotenv(find_dotenv())

from .responses import General as R
import warnings
import logging

from telegram import ForceReply, Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

bot = Bot(token=os.environ.get('JIRA_BOT_TOKEN'))
CHAT_ID = os.environ.get('TELEGRAM_JIRA_CHAT_ID')
MSG_THREAD_ID = os.environ.get('TELEGRAM_JIRA_MSG_THREAD_ID')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    warnings.filterwarnings('ignore')
    
    id = update.message.chat.id
    tname = str(update.effective_chat.first_name)
    text = str(update.message.text).replace(" ", "").lower()
    print(f'[{tname}/{id}] {text}')
    if text == "jira.noupdate":
        print(context)
        print(update.message)
        resp = await R.no_comment(update.message.from_user)
        
        await bot.send_message(chat_id=CHAT_ID, text=resp, message_thread_id=MSG_THREAD_ID)

def main():
    token = os.environ.get('JIRA_BOT_TOKEN')
    application = Application.builder().token(token).build()

    application.add_handler(MessageHandler(filters.TEXT, handle_message))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

    # return application