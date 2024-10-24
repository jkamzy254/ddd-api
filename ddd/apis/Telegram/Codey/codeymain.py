from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

from .responses import Responses as R
import warnings
import logging

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


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    warnings.filterwarnings('ignore')
    id = update.message.chat.id
    tname = str(update.effective_chat.first_name)
    text = str(update.message.text)
    print(f'[{tname}/{id}] {text}')
    response = R.bot_responses(id,tname,text)
    if isinstance(response, list):
        response,new_message,recipient_id = response
        pm = 'Markdown' if new_message.startswith('Telegram user') else 'HTML'
        await bot.sendMessage(chat_id=recipient_id, text=new_message, parse_mode=pm)
    if len(response) <= 4096:
        await update.message.reply_text(response, parse_mode='HTML') 
    elif len(response) <= 49152:
        response = response.replace('<b>','').replace('</b>','').replace('<i>','').replace('</i>','').replace('<u>','').replace('</u>','').replace('<pre>','').replace('</pre>','')
        await update.message.reply_text(f'<pre>{response[:4096]}</pre>', parse_mode='HTML')
        await update.message.reply_text(f'<pre>{response[4096:8192]}</pre>', parse_mode='HTML')
        await update.message.reply_text(f'<pre>{response[8192:12288]}</pre>', parse_mode='HTML')
        await update.message.reply_text(f'<pre>{response[12288:16384]}</pre>', parse_mode='HTML')
        await update.message.reply_text(f'<pre>{response[16384:20480]}</pre>', parse_mode='HTML')
        await update.message.reply_text(f'<pre>{response[20480:24576]}</pre>', parse_mode='HTML')
        await update.message.reply_text(f'<pre>{response[24576:28672]}</pre>', parse_mode='HTML')
        await update.message.reply_text(f'<pre>{response[28672:32768]}</pre>', parse_mode='HTML')
        await update.message.reply_text(f'<pre>{response[32768:36864]}</pre>', parse_mode='HTML')
        await update.message.reply_text(f'<pre>{response[36864:40960]}</pre>', parse_mode='HTML')
        await update.message.reply_text(f'<pre>{response[40960:45056]}</pre>', parse_mode='HTML')
        await update.message.reply_text(f'<pre>{response[45056:]}</pre>', parse_mode='HTML')
    else:
        await update.message.reply_text("Maximum character limit (49152) exceeeded", parse_mode='HTML')



def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    token = os.environ.get('CODEY_BOT_TOKEN')
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    # application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

    return application


# if __name__ == "__main__":
#     main()