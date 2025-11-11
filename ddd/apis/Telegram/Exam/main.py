from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

from .responses import general as g, scheduled as s
import warnings
import logging

from telegram import ForceReply, Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

bot = Bot(token=os.environ.get('EXAM_BOT_TOKEN'))

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
        rf"Hey marker {user.mention_html()}! Welcome to the DDD Exam Reporting Bot",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

async def get_excel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    file_path, exam_title, file_name, score_txt, chart_path = await g.get_scores('Yes')

    # Send the exam title and progress message last
    await update.message.reply_text(
        f"<b>{exam_title}</b>\nPreparing your report...",
        parse_mode='HTML'
    )

    # Send confirmation message
    score_parts = score_txt.split('\n\n')

    for part in score_parts:
        part = part.strip()
        if not part:
            continue

        # If a chunk is too long, split further by character length
        while len(part) > 4000:
            await update.message.reply_text(part[:4000], parse_mode='HTML')
            part = part[4000:]

        await update.message.reply_text(part, parse_mode='HTML')
    # Send confirmation message
    await update.message.reply_text(
        f"<b>{exam_title}</b>\nPreparing your report...",
        parse_mode='HTML'
    )
    
    
    await update.message.reply_photo(
        photo=open(chart_path, "rb"),
        caption=f"<b>{exam_title}</b>\n📊 Exam Summary by Department",
        parse_mode='HTML'
    )

    # Send the Excel file with custom download name
    with open(file_path, "rb") as f:
        await update.message.reply_document(
            document=f,
            filename=file_name,  # 👈 this sets the visible filename
            caption=f"<b>{exam_title}</b>",
            parse_mode='HTML'
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    warnings.filterwarnings('ignore')
    id = update.message.chat.id
    tname = str(update.effective_chat.first_name)
    text = update.message.text.strip()
    response = await g.report_score(text)
    await update.message.reply_text(response, parse_mode='HTML') 



def main():
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    token = os.environ.get('EXAM_BOT_TOKEN')
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("getexcel", get_excel))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    # application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

    return application


# if __name__ == "__main__":
#     main()