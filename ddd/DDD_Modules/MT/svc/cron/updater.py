from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from .job import svc_set_absent, svc_update

def start():
    local_tz = timezone('Australia/Melbourne')
    scheduler = BackgroundScheduler(timezone=local_tz)

    scheduler.add_job(svc_set_absent, CronTrigger(hour=3, timezone=local_tz))
    scheduler.add_job(svc_update, CronTrigger(hour=3, timezone=local_tz))

    scheduler.start()
