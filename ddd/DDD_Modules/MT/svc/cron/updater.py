from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .job import SVCSetAbsent

def start():
	scheduler = BackgroundScheduler() 
	scheduler.add_job(SVCSetAbsent, 'cron', hour=1)
	scheduler.start()