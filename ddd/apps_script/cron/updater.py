from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .job import ct_add_classes

def start():
	scheduler = BackgroundScheduler() 
	scheduler.add_job(ct_add_classes, 'cron', hour=1)
	scheduler.start()