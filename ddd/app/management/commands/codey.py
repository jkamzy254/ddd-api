from django.core.management import BaseCommand
from threading import Thread  # Or use multiprocessing for separate process

from apis.telegram_service.codeymain import main

class Command(BaseCommand):
    help = "This is our Telegram bot"
    
    def handle(self, *args, **options):
        # bot_thread = Thread(target=main)
        # bot_thread.daemon = True  # Allows bot to be stopped when main thread stops
        # bot_thread.start()
        main()