# =============================================================================
# ddd/apps_script/cron/updater.py  —  register it
# =============================================================================

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from .job import ct_add_classes, ct_transfer_run_due


def start():
    local_tz = timezone('Australia/Melbourne')
    scheduler = BackgroundScheduler(timezone=local_tz)

    scheduler.add_job(
        ct_add_classes,
        CronTrigger(hour=2, timezone=local_tz),
        id='ct_add_classes',
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    # 15 minutes after the class roll, so the two never overlap and the log
    # reads in the order things happened.
    scheduler.add_job(
        ct_transfer_run_due,
        CronTrigger(hour=2, minute=15, timezone=local_tz),
        id='ct_transfer_run_due',
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()


# =============================================================================
# Notes
# =============================================================================

"""
1. Timezone

   Australia/Melbourne and dbo.today()'s 'AUS Eastern Standard Time' are the
   same offset, including through daylight saving. So the scheduler's idea of
   "today" and the database's agree, and 02:00 local really is after midnight
   local. That is not true of most schedulers — it is true of yours because
   updater.py already passes an explicit tz. Worth not losing.

2. ready() runs once per worker process

   AppsScriptConfig.ready() fires in every process Django starts. Under
   Gunicorn with four workers you get four BackgroundSchedulers, and every job
   fires four times at 02:00. `max_instances=1` above only guards within one
   scheduler, not across processes.

   For ct_transfer_run_due this is now safe regardless: spCTTransferApply
   claims each row with

       UPDATE ... SET Status = 'Applied'
       OUTPUT deleted.* INTO @Claim
       WHERE ID = @TransferID AND Status = 'Approved';

   Only one UPDATE can match, so exactly one worker does the surgery and the
   other three fall through. That guard is in 02_transfers.sql specifically
   because of this.

   ct_add_classes has no such guard. Whether four concurrent
   spCTScheduleAddClasses calls are safe depends on that procedure — worth
   checking, separately from this work.

   If you would rather only one process schedules anything, the usual guard is:

       import os, sys

       def ready(self):
           # runserver spawns a reloader parent and a child; only the child
           # has RUN_MAIN set. Under Gunicorn neither is set, so gate on an
           # explicit env var you set for one worker, or use --preload.
           if os.environ.get('RUN_MAIN') != 'true' and 'runserver' in sys.argv:
               return
           from .cron import updater
           updater.start()

   That is a bigger change than this task needs. The atomic claim is the
   robust fix; the env guard is tidiness.

3. If you want it more often than daily

   Swap the trigger for CronTrigger(minute=5) to run hourly at five past. The
   procedure costs a scan of an empty set when nothing is due, so this is
   cheap. Daily at 02:00 is sufficient for correctness — only future-dated
   transfers wait, and they come due at midnight.

4. You do not need the Apps Script trigger

   Code.js also ships applyDueTransfers() and installTransferTrigger() as an
   alternative for a deployment with no Django cron. Do not install that
   trigger as well — running both is harmless thanks to the claim, but it is
   two things to remember instead of one. applyDueTransfers() is still useful
   on its own for a manual kick from the editor, and testRunDue() confirms the
   endpoint is routed.

5. The one query worth keeping

       SELECT ID, UID, Kind, EffectiveDate, Status
       FROM dbo.CTTransferLogTable
       WHERE Status = 'Approved' AND EffectiveDate <= dbo.today();

   Should be empty every morning after 02:15. Rows persisting there is the only
   symptom of the job not running — the log still reads 'Approved' and the UI
   still shows the transfer as scheduled, so nothing else surfaces it.
"""
