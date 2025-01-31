from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .job import edu_set_absent

def start():
	scheduler = BackgroundScheduler() 
	scheduler.add_job(edu_set_absent, 'cron', hour=1)
	scheduler.start()