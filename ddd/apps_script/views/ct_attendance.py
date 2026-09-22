from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection

import json
import pandas as pd

# Create your views here.


        
class GetMemberViewSet(APIView):
    def get(self, request):
        username = request.GET.get('username')
        password = request.GET.get('password')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spCTLogin @Username = '{username}', @Password = '{password}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            if len(result) == 0:
                return Response({'error': 'Unauthorized Access'}, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CTGetAttendanceSummaryViewSet(APIView):
    def get(self, request):
        uid = request.GET.get("UID")
        period = request.GET.get("Period")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spCTGetAttendanceSummary @TGW = '{uid}', @Period = '{period}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class CTGetStudentListViewSet(APIView):
    def get(self, request):
        uid = request.GET.get("UID")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spCTGetStudents {uid}")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class CTSummaryGetAllDaysViewSet(APIView):
    def get(self, request):
        uid = request.GET.get("UID")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spCTSummaryGetAllDays {uid}")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CTSummaryGetClassViewSet(APIView):
    def get(self, request):
        ctid = request.GET.get("CTID")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spCTSummaryGetClass {ctid}")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class CTSummaryGetClassSummaryViewSet(APIView):
    def get(self, request):
        ctid = request.GET.get("CTID")
        uid = request.GET.get("UID")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spCTSummaryGetClassSummary @CTDayID = {ctid}, @TGW = '{uid}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class CTGetAttendanceViewSet(APIView):
    def get(self, request):
        uid = request.GET.get("UID")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spCTGetStudentAttendance {uid}")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CTGetStudHistoryViewSet(APIView):
    def get(self, request):
        uid = request.GET.get("UID")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spCTGetStudHistory {uid}")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CTGetStudentViewSet(APIView):
    def get(self, request):
        uid = request.GET.get("UID")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spCTGetStudent {uid}")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class CTGetWeeklyScheduleViewSet(APIView):
    def get(self, request):
        uid = request.GET.get("UID")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spCTGetSchedule {uid}")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class CTUpdateScheduleViewSet(APIView):
    def post(self, request):
        data = request.data
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spCTUpdateSchedule @CTID = {data.get('CTID')}, @Date = '{data.get('Date')}', @Topic = '{data.get('Topic')}'")
                result = f"Update for CT Day {data.get('Date')} done"

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class CTUpdateAttendanceViewSet(APIView):
    def post(self, request):
        rec = request.data
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""EXEC spCTUpdateAttendance 
                    @UID = '{rec.get('UID')}', @Attendance = '{rec.get('Attendance')}', @ID = {rec.get('ID')}, @Reason = {"'"+rec.get('Reason').replace("'","''")+"'" if rec.get('Reason') else "NULL"}
                """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        

class CTScheduleAddDaysViewSet(APIView):
    def post(self, request):
        rec = request.data
        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spCTScheduleAddClasses")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
class CTGetCCTTransitionViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spBBGetCCTTransition {uid}")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class CTGetTransitionCTDetsViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spBBGetTransitionCTDets {uid}")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

        
class UpdateTransitionCTViewSet(APIView):
    def post(self, request):
        data =request.data
        uid = data.get('UID')
        textBBT = data.get('TextBBT')
        ctCardCT = data.get('CTCardCT')
        bltDone = data.get('BLTDone')
        bltJDSN =   data.get('BLTJDSN')
        hmrmJDSN = data.get('HmrmJDSN')
        intDone = data.get('IntDone')
        intDT = data.get('IntDT').replace("'","''")
        reaction = data.get('Reaction').replace("'","''")

        try:
            with connection.cursor() as cursor:
                
                cursor.execute(f"""EXEC spBBUpdateTransitionCT 
                                    @UID = '{uid}', 
                                    @TextBBT = '{textBBT}', 
                                    @CTCardCT = '{ctCardCT}', 
                                    @BLTDone = '{bltDone}', 
                                    @BLTJDSN = '{bltJDSN}', 
                                    @HmrmJDSN = '{hmrmJDSN}', 
                                    @IntDone = '{intDone}', 
                                    @IntDT = '{intDT}', 
                                    @Reaction = '{reaction}'
                               """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


"""
New CT endpoints — names, inactive reasons, transfers.

Written with bound parameters rather than f-string interpolation. pyodbc sends
these as real parameters, so quoting and escaping stop being the caller's
problem: no .replace("'","''"), no NULL special-casing, and no way for a value
to change the shape of the statement.

Drop these into the same views.py as the existing classes and route them:

    path('ctUpdateStudentName/',   CTUpdateStudentNameViewSet.as_view()),
    path('ctGetInactiveReasons/',  CTGetInactiveReasonsViewSet.as_view()),
    path('ctGetTransferOptions/',  CTGetTransferOptionsViewSet.as_view()),
    path('ctGetTransfers/',        CTGetTransfersViewSet.as_view()),
    path('ctCreateTransfer/',      CTCreateTransferViewSet.as_view()),
    path('ctResolveTransfer/',     CTResolveTransferViewSet.as_view()),
"""


def call_proc(sql, params):
    """Runs a stored procedure and returns its first result set as dicts."""
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        if cursor.description is None:
            return []
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]



class CTUpdateStudentNameViewSet(APIView):
    def post(self, request):
        rec = request.data
        try:
            result = call_proc(
                "EXEC spCTUpdateStudentName "
                "@UID = %s, @ID = %s, @FirstName = %s, @MiddleName = %s, "
                "@LastName = %s, @PrefName = %s, @UpdatedBy = %s",
                [
                    rec.get('UID'),
                    rec.get('ID'),
                    rec.get('FirstName'),
                    rec.get('MiddleName') or None,
                    rec.get('LastName') or None,
                    rec.get('PrefName') or None,
                    rec.get('UpdatedBy') or None,
                ],
            )
            if not result:
                return Response({'error': 'No student with that UID'},
                                status=status.HTTP_404_NOT_FOUND)
            return Response(result[0], status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CTGetInactiveReasonsViewSet(APIView):
    def get(self, request):
        try:
            return Response(call_proc("EXEC spCTGetInactiveReasons", []),
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CTGetTransferOptionsViewSet(APIView):
    def get(self, request):
        try:
            result = call_proc("EXEC spCTGetTransferOptions @UID = %s",
                               [request.GET.get('UID')])
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CTGetTransfersViewSet(APIView):
    def get(self, request):
        try:
            result = call_proc(
                "EXEC spCTGetTransfers @UID = %s, @Scope = %s",
                [request.GET.get('UID'), request.GET.get('Scope') or 'Pending'],
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CTCreateTransferViewSet(APIView):
    def post(self, request):
        rec = request.data

        # Apps Script already joins the UIDs, but accept a list too so the
        # endpoint is usable from anything else.
        students = rec.get('Students')
        if isinstance(students, (list, tuple)):
            students = ','.join(str(s).strip() for s in students if str(s).strip())

        if not students:
            return Response({'error': 'No students were supplied'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            result = call_proc(
                "EXEC spCTCreateTransfer "
                "@Students = %s, @Kind = %s, @ToTGWID = %s, @ToCTID = %s, "
                "@ToClassID = %s, @EffectiveDate = %s, @Reason = %s, @RequestedBy = %s",
                [
                    students,
                    rec.get('Kind'),
                    rec.get('ToTGWID'),
                    rec.get('ToCTID'),
                    rec.get('ToClassID'),
                    rec.get('EffectiveDate'),
                    rec.get('Reason') or None,
                    rec.get('RequestedBy'),
                ],
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CTAdminOverviewViewSet(APIView):
    """Every session scored for an admin (principal / secretary / IT), with a ProxyUID each."""

    def get(self, request):
        finished = str(request.GET.get('Finished', '0')).lower() in ('1', 'true', 'yes')
        try:
            result = call_proc(
                "EXEC spCTAdminOverview @UID = %s, @IncludeFinished = %s",
                [request.GET.get('UID'), 1 if finished else 0],
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class CTCloseFinishedViewSet(APIView):
    """
    Nightly tidy: sessions past their EndDate become inactive, their open
    staff rows close on that date, courses whose sessions have all ended
    become inactive. See spCTCloseFinished for the exact rules.

    GET  ?dry=1            report only
    POST {students: true}  also close student schedule rows (off by default)
    """

    def get(self, request):
        return self._run(dry=True, students=False)

    def post(self, request):
        rec = request.data or {}
        return self._run(dry=str(rec.get('dry', '0')).lower() in ('1', 'true'),
                         students=str(rec.get('students', '0')).lower() in ('1', 'true'))

    def _run(self, dry, students):
        try:
            result = call_proc(
                "EXEC spCTCloseFinished @DryRun = %s, @CloseStaff = 1, @CloseStudents = %s",
                [1 if dry else 0, 1 if students else 0],
            )
            return Response(result[0] if result else {'Res': 'No response', 'Ok': 0},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CTTransferRunDueViewSet(APIView):
    """
    Applies approved transfers whose effective date has arrived.

    Azure SQL Database has no SQL Server Agent, so this is called on a schedule
    from outside — see applyDueTransfers() and installTransferTrigger() in
    Code.js. It is idempotent, so an extra call costs a scan of an empty set.

    spCTTransferRunDue returns exactly one summary row (Due, Applied, Failed,
    RunAt, Res, Ok) because it calls spCTTransferApply with @Quiet = 1 — without
    that it would emit one rowset per transfer and this view would report a
    single transfer's outcome as the whole run's.
    """

    def post(self, request):
        try:
            result = call_proc("EXEC spCTTransferRunDue", [])
            if not result:
                return Response({'Due': 0, 'Applied': 0, 'Failed': 0,
                                 'Res': 'Nothing due.', 'Ok': 1},
                                status=status.HTTP_200_OK)
            return Response(result[0], status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CTResolveTransferViewSet(APIView):
    def post(self, request):
        rec = request.data

        ids = rec.get('TransferIDs')
        if isinstance(ids, (list, tuple)):
            ids = ','.join(str(i).strip() for i in ids if str(i).strip())

        if not ids:
            return Response({'error': 'No transfers were supplied'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            result = call_proc(
                "EXEC spCTResolveTransfer "
                "@TransferIDs = %s, @Action = %s, @Note = %s, @ResolvedBy = %s",
                [
                    ids,
                    rec.get('Action'),
                    rec.get('Note') or None,
                    rec.get('ResolvedBy'),
                ],
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ---------------------------------------------------------------------------
# The existing CTUpdateStudentStatusViewSet, rewritten for the new parameters.
# Replace the current class with this one.
# ---------------------------------------------------------------------------

class CTUpdateStudentStatusViewSet(APIView):
    def post(self, request):
        rec = request.data
        try:
            result = call_proc(
                "EXEC spCTUpdateStudentStatus "
                "@UID = %s, @Registration = %s, @Status = %s, @StudName = %s, @ID = %s, "
                "@InactiveDate = %s, @Reasons = %s, @PrimaryReason = %s, "
                "@Proceedable = %s, @NonProceedReason = %s, "
                "@ReturnDate = %s, @Notes = %s, @UpdatedBy = %s",
                [
                    rec.get('UID'),
                    rec.get('Registration'),
                    rec.get('Status'),
                    rec.get('StudName'),
                    rec.get('ID'),
                    rec.get('InactiveDate') or None,
                    rec.get('Reasons') or None,
                    rec.get('PrimaryReason') or None,
                    1 if rec.get('Proceedable') in (1, '1', True, None) else 0,
                    rec.get('NonProceedReason') or None,
                    rec.get('ReturnDate') or None,
                    rec.get('Notes') or None,
                    rec.get('UpdatedBy') or None,
                ],
            )
            if not result:
                return Response({'error': 'No student with that UID'},
                                status=status.HTTP_404_NOT_FOUND)
            return Response(result[0], status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CTStaffCatalogueViewSet(APIView):
    """Courses, sessions, current staff allocations and allocatable members, as JSON columns."""

    def get(self, request):
        finished = str(request.GET.get('Finished', '0')).lower() in ('1', 'true', 'yes')
        try:
            result = call_proc(
                "EXEC spCTStaffCatalogue @UID = %s, @IncludeFinished = %s",
                [request.GET.get('UID'), 1 if finished else 0],
            )
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CTStaffAllocateViewSet(APIView):
    """Add | Transfer | End a staff member on a session. See spCTStaffAllocate."""

    def post(self, request):
        rec = request.data
        try:
            result = call_proc(
                "EXEC spCTStaffAllocate "
                "@ActorUID = %s, @StaffUID = %s, @Mode = %s, @ToCTID = %s, @FromCTID = %s, "
                "@NumRole = %s, @EffectiveDate = %s, @ReassignTo = %s, @Note = %s",
                [
                    rec.get('ActorUID'),
                    rec.get('StaffUID'),
                    rec.get('Mode'),
                    rec.get('ToCTID'),
                    rec.get('FromCTID'),
                    rec.get('NumRole'),
                    rec.get('EffectiveDate') or None,
                    rec.get('ReassignTo') or None,
                    rec.get('Note') or None,
                ],
            )
            return Response(result[0] if result else {'Res': 'No response', 'Ok': 0},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CTCourseSaveViewSet(APIView):
    def post(self, request):
        rec = request.data
        try:
            result = call_proc(
                "EXEC spCTCourseSave @ActorUID = %s, @ID = %s, @Name = %s, "
                "@Is_Active = %s, @StartDate = %s, @EndDate = %s",
                [
                    rec.get('ActorUID'),
                    rec.get('ID'),
                    rec.get('Name'),
                    1 if rec.get('Is_Active') in (1, '1', True, None) else 0,
                    rec.get('StartDate') or None,
                    rec.get('EndDate') or None,
                ],
            )
            return Response(result[0] if result else {'Res': 'No response', 'Ok': 0},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CTSessionSaveViewSet(APIView):
    def post(self, request):
        rec = request.data
        try:
            result = call_proc(
                "EXEC spCTSessionSave @ActorUID = %s, @ID = %s, @ClassID = %s, @Name = %s, "
                "@Season = %s, @CTSched = %s, @Is_Active = %s, @StartDate = %s, "
                "@EndDate = %s, @SunClass = %s",
                [
                    rec.get('ActorUID'),
                    rec.get('ID'),
                    rec.get('ClassID'),
                    rec.get('Name'),
                    rec.get('Season'),
                    rec.get('CTSched') or None,
                    1 if rec.get('Is_Active') in (1, '1', True, None) else 0,
                    rec.get('StartDate') or None,
                    rec.get('EndDate') or None,
                    None if rec.get('SunClass') in (None, '') else (1 if rec.get('SunClass') in (1, '1', True) else 0),
                ],
            )
            return Response(result[0] if result else {'Res': 'No response', 'Ok': 0},
                            status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

