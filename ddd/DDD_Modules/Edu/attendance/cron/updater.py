from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .job import edu_set_absent, edu_update_expected, edu_update_actual, print_awesome

def start():
	scheduler = BackgroundScheduler() 
	scheduler.add_job(edu_set_absent, 'cron', hour=1)
	scheduler.add_job(edu_update_expected, 'cron', hour=1)
	scheduler.add_job(edu_update_actual, 'cron', hour=1)
	scheduler.add_job(print_awesome, 'cron', hour=19, minute=41)
	scheduler.start()