from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

from .responses import Responses as R
import warnings
import logging
import re

from telegram import ForceReply, Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

bot = Bot(token=os.environ.get('CODEY_BOT_TOKEN'))

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




async def handle_message(update, context):
    warnings.filterwarnings('ignore')
    id = update.message.chat.id
    tname = str(update.effective_chat.first_name)
    text = str(update.message.text)
    print(f'[{tname}/{id}] {text}')
    response = R.bot_responses(id, tname, text)

    if isinstance(response, list):
        print(response)
        response, new_message, recipient_id = response
        print(response)
        pm = 'Markdown' if new_message.startswith('Telegram user') else 'HTML'
        print(f"Parse_mode = {pm}")
        await bot.sendMessage(chat_id=recipient_id, text=new_message, parse_mode=pm)
    else:
        PREFIXES = ('Markdown@@', 'MarkdownV2@@', 'HTML@@')
        if response.startswith(PREFIXES):
            pm, _, response = response.partition('@@')
        else:
            pm = 'HTML'

    if len(response) <= 4096:
        if pm in ('Markdown', 'MarkdownV2'):
            print(f'Using {pm}')
            replacements = [('<b>','*'),('</b>','*'),('<i>','_'),('</i>','_'),('<pre>','```'),('</pre>','```')]
            if pm == 'MarkdownV2':
                replacements += [('<u>','__'),('</u>','__')]
            else:
                replacements += [('<u>',''),('</u>','')]
            for old, new in replacements:
                response = response.replace(old, new)
            await update.message.reply_text(response, parse_mode=pm)
        else:
            print('Using HTML')
            await update.message.reply_text(response, parse_mode='HTML')

    elif len(response) <= 49152:
        print('Splitting message into chunks of 4096 characters due to Telegram limit')
        response = re.sub(r'</?(?:b|i|u|pre)>', '', response)
        # Only send chunks that actually have content
        for i in range(0, len(response), 4096):
            chunk = response[i:i+4096]
            if chunk:
                await update.message.reply_text(f'<pre>{chunk}</pre>', parse_mode='HTML')
    else:
        await update.message.reply_text("Maximum character limit (49152) exceeded", parse_mode='HTML')






def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    token = os.environ.get('CODEY_BOT_TOKEN')
    application = Application.builder().token(token).concurrent_updates(True).build()

    # on different commands - answer in Telegram
    # application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

    return application


# if __name__ == "__main__":
#     main()