from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

from .responses import general as g, scheduled as s, hsp as h, sep as sp
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

NO_EXAM_MSG = "No eligible exam record found."


async def send_long_text(update: Update, text: str) -> None:
    # Telegram messages max out at 4096 chars, so send per department block
    for part in text.split('\n\n'):
        part = part.strip()
        if not part:
            continue

        # If a chunk is too long, split further by character length
        while len(part) > 4000:
            await update.message.reply_text(part[:4000], parse_mode='HTML')
            part = part[4000:]

        await update.message.reply_text(part, parse_mode='HTML')


def score_command(exam):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        exam_title, score_txt = await exam.get_scores()
        if not exam_title:
            await update.message.reply_text(score_txt)
            return

        await update.message.reply_text(f"<b>{exam_title}</b>\nFetching scores...", parse_mode='HTML')
        await send_long_text(update, score_txt)
    return handler


def excel_command(exam):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Preparing your Excel report...")
        report = await exam.get_excel_report()
        if not report:
            await update.message.reply_text(NO_EXAM_MSG)
            return

        file_path, exam_title, file_name = report
        # Send the Excel file with custom download name
        with open(file_path, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=file_name,  # 👈 this sets the visible filename
                caption=f"<b>{exam_title}</b>",
                parse_mode='HTML'
            )
        os.remove(file_path)
    return handler


def chart_command(exam):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await update.message.reply_text("Preparing your chart...")
        report = await exam.get_chart_report()
        if not report:
            await update.message.reply_text(NO_EXAM_MSG)
            return

        chart_path, exam_title = report
        with open(chart_path, "rb") as f:
            await update.message.reply_photo(
                photo=f,
                caption=f"<b>{exam_title}</b>\n📊 Exam Summary by Department",
                parse_mode='HTML'
            )
    return handler


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

    # /getscore, /getexcel, /getchart plus /gethsp... and /getsep... variants
    for prefix, exam in (("", g), ("hsp", h), ("sep", sp)):
        application.add_handler(CommandHandler(f"get{prefix}score", score_command(exam)))
        application.add_handler(CommandHandler(f"get{prefix}excel", excel_command(exam)))
        application.add_handler(CommandHandler(f"get{prefix}chart", chart_command(exam)))

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