from django.core.management import BaseCommand


from apis.Telegram.Codey.main import main as codey_main
from apis.Telegram.Jira.main import main as jira_main
from apis.Telegram.SuperGroup.main import main as sgcheck_main
from apis.Telegram.Exam.main import main as exam_main
from apis.Telegram.MaterialUpload.main import main as material_main


class Command(BaseCommand):
    help = "Start all Telegram bots."
    

    def handle(self, *args, **options):
        from multiprocessing import Process
        codey_process = Process(target=codey_main)
        jira_process = Process(target=jira_main)
        sgcheck_process = Process(target=sgcheck_main)
        exam_process = Process(target=exam_main)
        mupload_process = Process(target=material_main)

        codey_process.start()
        jira_process.start()
        sgcheck_process.start()
        exam_process.start()
        mupload_process.start()

        codey_process.join()
        jira_process.join()
        sgcheck_process.join()
        exam_process.join()
        mupload_process.join()
