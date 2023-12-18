from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv())

TOKEN = os.environ.get('TELEGRAM_TOKEN')
BOT_URL = 'https://t.me/tut_teleg_bot'