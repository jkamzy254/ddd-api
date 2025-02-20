from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .job import svc_set_absent, svc_update

def start():
	scheduler = BackgroundScheduler() 
	scheduler.add_job(svc_set_absent, 'cron', hour=12)
	scheduler.add_job(svc_update, 'cron', hour=12)
	scheduler.start()