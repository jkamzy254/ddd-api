"""
Scheduling spCTTransferRunDue from the APScheduler setup you already have.

Azure SQL Database has no SQL Server Agent and no msdb, so the scheduler has to
live outside the database. You already run one: apps_script/cron/updater.py
starts a BackgroundScheduler from AppsScriptConfig.ready(). This adds one job to
it, in the same shape as ct_add_classes.

Two files change. Both diffs are below, then the notes that matter.
"""


# =============================================================================
# ddd/apps_script/cron/job.py  —  add ct_transfer_run_due below ct_add_classes
# =============================================================================

from django.db import connection


def ct_add_classes():
    print("Printing Connection as Cursor for spCTScheduleAddClasses")
    with connection.cursor() as cursor:
        cursor.execute("EXEC spCTScheduleAddClasses")
    print("Just ran Connection as Cursor for spCTScheduleAddClasses")


def ct_transfer_run_due():
    """
    Applies approved student transfers whose effective date has arrived.

    spCTCreateTransfer applies a same-day transfer immediately, so this only
    ever picks up future-dated ones — which become due at midnight, which is why
    a 02:00 run is early enough. Nobody reads a roster between midnight and 2am.

    Idempotent: it selects only Status = 'Approved' AND EffectiveDate <= today,
    and applying a row sets it to 'Applied'. Running it twice does the work once.

    Returns one summary row, so unlike ct_add_classes there is something worth
    printing.
    """
    with connection.cursor() as cursor:
        cursor.execute("EXEC spCTTransferRunDue")

        # No rowset at all would mean the proc bailed before its final SELECT.
        row = cursor.fetchone() if cursor.description else None

        if row is None:
            print("ct_transfer_run_due: no summary returned")
            return

        summary = dict(zip([c[0] for c in cursor.description], row))

    # Due / Applied / Failed / RunAt / Res / Ok
    print("ct_transfer_run_due: %s (due=%s applied=%s failed=%s)" % (
        summary.get("Res"), summary.get("Due"),
        summary.get("Applied"), summary.get("Failed"),
    ))

    if not summary.get("Ok"):
        # Left approved and past its date — the next run retries it, but this
        # is the line to grep for if a student is on the wrong roll.
        print("ct_transfer_run_due: SOME TRANSFERS DID NOT APPLY — check CTTransferLogTable")


