from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone

from .job import ct_add_classes, ct_transfer_run_due, ct_close_finished


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
        misfire_grace_time=3600,   # a restart at 02:14 should not skip the day
    )

    # Runs first so a session that ended yesterday is inactive before the
    # transfer job and the class roll look at it.
    scheduler.add_job(
        ct_close_finished,
        CronTrigger(hour=1, minute=45, timezone=local_tz),
        id='ct_close_finished',
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )

    scheduler.start()


# =============================================================================
# Notes
# =============================================================================

"""
1. Timezone — nothing to do, but worth not losing

   Australia/Melbourne and dbo.today()'s 'AUS Eastern Standard Time' are the
   same offset, including through daylight saving. So the scheduler's idea of
   "today" and the database's agree, and 02:15 local really is after local
   midnight. That is not true of most schedulers — it is true of yours because
   updater.py already passes an explicit tz.

2. The multi-worker race — solved, but not by this file

   AppsScriptConfig.ready() fires in every process Django starts. Under
   Gunicorn with four workers you get four BackgroundSchedulers, and every job
   fires four times at 02:00. `max_instances=1` guards within one scheduler
   only; it does nothing across processes.

   For ct_transfer_run_due that is safe, because spCTTransferApply claims each
   row before touching anything:

       UPDATE dbo.CTTransferLogTable
       SET Status = 'Applied', AppliedAt = SYSUTCDATETIME()
       OUTPUT deleted.UID, deleted.Kind, ... INTO @Claim
       WHERE ID = @TransferID AND Status = 'Approved';

       IF NOT EXISTS (SELECT 1 FROM @Claim) BEGIN ROLLBACK ... RETURN; END;

   Only one UPDATE can match, so one worker does the surgery and the rest fall
   through. That guard lives in 02_transfers.sql. Pasting this file without
   running the updated 02 leaves you unprotected.

3. ct_add_classes has no such guard — worth checking separately

   Four concurrent spCTScheduleAddClasses calls may be harmless or may create
   duplicate CT days. I have not seen that procedure, so I cannot say. The
   quickest check is whether CTScheduleLogTable has ever grown a duplicate
   (CTID, CTDate):

       SELECT CTID, CTDate, COUNT(*) AS Copies
       FROM dbo.CTScheduleLogTable
       GROUP BY CTID, CTDate
       HAVING COUNT(*) > 1;

   If that returns rows, the job has already been double-firing and it is the
   likely cause.

4. If you want only one process scheduling anything

   The RUN_MAIN check that gets quoted for this only works under `runserver` —
   Django's reloader sets it in the child process. Gunicorn sets nothing, so
   every worker still starts a scheduler. It is not the fix.

   The two that actually work:

   (a) Run the scheduler as its own process. A management command with a
       BlockingScheduler, deployed as a separate service or container, and
       ready() no longer starts anything:

           # apps_script/management/commands/run_cron.py
           from apscheduler.schedulers.blocking import BlockingScheduler
           from apscheduler.triggers.cron import CronTrigger
           from django.core.management.base import BaseCommand
           from pytz import timezone
           from apps_script.cron.job import ct_add_classes, ct_transfer_run_due

           class Command(BaseCommand):
               help = 'Runs the CT scheduled jobs. One instance only.'

               def handle(self, *args, **options):
                   tz = timezone('Australia/Melbourne')
                   sched = BlockingScheduler(timezone=tz)
                   sched.add_job(ct_add_classes,
                                 CronTrigger(hour=2, timezone=tz))
                   sched.add_job(ct_transfer_run_due,
                                 CronTrigger(hour=2, minute=15, timezone=tz))
                   sched.start()

       This is the textbook answer and it fixes ct_add_classes too. It costs
       you one more thing to deploy and keep running.

   (b) A SQL Server application lock, which works on Azure SQL Database:

           EXEC sp_getapplock @Resource = 'ct_cron', @LockMode = 'Exclusive',
                              @LockOwner = 'Session', @LockTimeout = 0;
           -- returns >= 0 if acquired, < 0 if another worker holds it
           ...
           EXEC sp_releaseapplock @Resource = 'ct_cron', @LockOwner = 'Session';

       Use @LockOwner = 'Session', NOT 'Transaction'. A transaction-scoped lock
       means running the job inside transaction.atomic(), and the unqualified
       ROLLBACK in spCTTransferApply would then tear down that outer
       transaction — see the docstring on ct_transfer_run_due.

   For transfers alone, neither is necessary: the atomic claim already makes a
   quadruple run correct. Do (a) if ct_add_classes turns out to need it.

5. If you want it more often than daily

   Swap the trigger for CronTrigger(minute=5) to run hourly at five past. The
   procedure costs a scan of an empty set when nothing is due. Daily at 02:15
   is sufficient for correctness — only future-dated transfers wait, and they
   come due at midnight.

6. You do not need the Apps Script trigger

   Code.js also ships applyDueTransfers() and installTransferTrigger() as an
   alternative for a deployment with no Django cron. Do not install that
   trigger as well — running both is harmless thanks to the claim, but it is
   two things to remember instead of one. applyDueTransfers() is still useful
   for a manual kick from the editor, and testRunDue() confirms the endpoint is
   routed.

7. The one query worth keeping

       SELECT ID, UID, Kind, EffectiveDate, Status
       FROM dbo.CTTransferLogTable
       WHERE Status = 'Approved' AND EffectiveDate <= dbo.today();

   Should be empty every morning after 02:15. Rows persisting there is the only
   symptom of the job not running — the log still reads 'Approved' and the UI
   still shows the transfer as scheduled, so nothing else surfaces it.
"""
