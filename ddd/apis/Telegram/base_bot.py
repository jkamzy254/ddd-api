import asyncio
import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters

class BaseBot:
    def __init__(self, token, name):
        self.bot = telegram.Bot(token=token)
        self.name = name
        self.dispatcher = self.bot.dispatcher

    async def start(self):
        # Common bot startup logic here (optional)
        pass

    async def handle_message(self, update, context):
        # Handle messages here
        # You can access the message text with update.message.text
        pass

    async def run(self):
        # Register custom handlers specific to each bot in subclasses
        # You can access the dispatcher through self.dispatcher

        # Start the bot
        await self.start()
        await self.dispatcher.start_polling()
        await self.dispatcher.wait_for_updates()

