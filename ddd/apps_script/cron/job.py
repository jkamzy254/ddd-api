from django.db import close_old_connections, connection


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
    a 02:15 run is early enough. Nobody reads a roster between midnight and 2am.

    Idempotent: it selects only Status = 'Approved' AND EffectiveDate <= today,
    and applying a row sets it to 'Applied'. Running it twice does the work once.

    DO NOT wrap this call in transaction.atomic(). spCTTransferApply issues an
    unqualified ROLLBACK TRANSACTION in its CATCH block, which rolls back to
    @@TRANCOUNT 0 — destroying an outer transaction rather than just its own.
    Django's COMMIT would then fail with error 3902. The procedure manages its
    own transaction per transfer; it does not need one around it.
    """
    # A scheduler thread lives for the life of the process and never goes
    # through Django's request cycle, so nothing ever closes its connection.
    # After 24 hours idle the server has usually dropped it, and the 02:15 run
    # dies on a closed connection. Reaping first costs nothing and removes a
    # failure that only shows up in production, overnight, intermittently.
    close_old_connections()

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


def ct_close_finished():
    """
    Sessions past their EndDate become inactive; their open staff rows close
    on that date; courses whose sessions have all ended become inactive.
    Idempotent — see spCTCloseFinished. Student schedule rows are left alone
    here; pass @CloseStudents = 1 once you have seen a dry run.
    """
    close_old_connections()

    with connection.cursor() as cursor:
        cursor.execute("EXEC spCTCloseFinished @DryRun = 0, @CloseStaff = 1, @CloseStudents = 0")
        row = cursor.fetchone() if cursor.description else None
        if row is None:
            print("ct_close_finished: no summary returned")
            return
        summary = dict(zip([c[0] for c in cursor.description], row))

    print("ct_close_finished: %s" % summary.get("Res"))