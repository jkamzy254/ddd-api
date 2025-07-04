from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
from .job import ct_add_classes, cron_test_AS

def start():
    local_tz = timezone('Australia/Melbourne')
    scheduler = BackgroundScheduler(timezone=local_tz)

    scheduler.add_job(ct_add_classes, CronTrigger(hour=2, timezone=local_tz))
    scheduler.add_job(ct_add_classes, CronTrigger(hour=22, minute=41, timezone=local_tz))
    scheduler.add_job(cron_test_AS, CronTrigger(hour=23, minute=20, timezone=local_tz))

    scheduler.start()
