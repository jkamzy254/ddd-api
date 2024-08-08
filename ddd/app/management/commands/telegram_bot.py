from django.core.management import BaseCommand


from apis.Telegram.Codey.codeymain import main as codey_main
from apis.Telegram.Jira.jiramain import main as jira_main


class Command(BaseCommand):
    help = "Start both Telegram bots."
    

    def handle(self, *args, **options):
        from multiprocessing import Process
        codey_process = Process(target=codey_main)
        jira_process = Process(target=jira_main)

        codey_process.start()
        jira_process.start()

        codey_process.join()
        jira_process.join()
