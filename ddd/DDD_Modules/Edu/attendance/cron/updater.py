from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone  # add this
from .job import edu_set_absent, edu_update_expected, edu_update_actual, print_awesome

def start():
	scheduler = BackgroundScheduler(timezone=timezone('Australia/Melbourne'))  # set timezone
	
	scheduler.add_job(edu_set_absent, CronTrigger(hour=3, timezone=timezone('Australia/Melbourne')))
	scheduler.add_job(edu_update_expected, CronTrigger(hour=3, timezone=timezone('Australia/Melbourne')))
	scheduler.add_job(edu_update_actual, CronTrigger(hour=3, timezone=timezone('Australia/Melbourne')))
	# scheduler.add_job(print_awesome, CronTrigger(hour=19, minute=44, timezone=timezone('Australia/Melbourne')))

	scheduler.start()
