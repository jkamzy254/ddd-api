from django.core.management import BaseCommand


from apis.Telegram.Codey.codeymain import main as codey_main
from apis.Telegram.Jira.jiramain import main as jira_main
from apis.Telegram.SuperGroup.sgcheckmain import main as sgcheck_main


class Command(BaseCommand):
    help = "Start both Telegram bots."
    

    def handle(self, *args, **options):
        from multiprocessing import Process
        codey_process = Process(target=codey_main)
        jira_process = Process(target=jira_main)
        sgcheck_process = Process(target=sgcheck_main)

        codey_process.start()
        jira_process.start()
        sgcheck_process.start()

        codey_process.join()
        jira_process.join()
        sgcheck_process.join()
