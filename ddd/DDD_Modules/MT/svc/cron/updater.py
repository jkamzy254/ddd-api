from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .job import svc_set_absent

def start():
	scheduler = BackgroundScheduler() 
	scheduler.add_job(svc_set_absent, 'cron', hour=1)
	scheduler.start()