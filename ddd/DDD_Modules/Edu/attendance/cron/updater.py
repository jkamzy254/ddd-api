from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .job import EduSetAbsent

def start():
	scheduler = BackgroundScheduler() 
	scheduler.add_job(EduSetAbsent, 'cron', hour=1)
	scheduler.start()