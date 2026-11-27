import asyncio

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

import warnings
import logging
import re
import html
import traceback

from telegram import ForceReply, Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from .responses.ct_report_handler import ptb_ct_report_button, ptb_ct_report_command

bot = Bot(token=os.environ.get('CENTRI_BOT_TOKEN')) # type: ignore

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




def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    token = os.environ.get('CENTRI_BOT_TOKEN')
    application = Application.builder().token(token).concurrent_updates(True).build()

    # on different commands - answer in Telegram
    # application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    # Church Regrouping Accept/Decline buttons (crg:a:<id> / crg:d:<id>). Keep this ahead of
    # any CallbackQueryHandler added later without a pattern, or it would take these presses.
    application.add_handler(CommandHandler(['ctreport', 'ctgroup'], ptb_ct_report_command))
    application.add_handler(CallbackQueryHandler(ptb_ct_report_button, pattern=r'^ctr:'))

    # Run the bot until the user presses Ctrl-C
    # application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

    return application


# if __name__ == "__main__":
#     main()