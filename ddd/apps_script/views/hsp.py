from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection

from django.conf import settings
import hmac

import json
import pandas as pd
from datetime import date, datetime

# Create your views here.


        
class GetMemberViewSet(APIView):
    def get(self, request):
        username = request.GET.get('username')
        password = request.GET.get('password')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM NewEduASLoginFunction(%s, %s)", [username,password])
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            if len(result) == 0:
                return Response({'error': 'Unauthorized Access'}, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class HSPGetFoldersViewSet(APIView):
    def get(self, request):
        uid = request.GET.get("UID")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spEduVideoGetFolders @User = '{uid}'")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class HSPGetMaterialViewSet(APIView):
    def get(self, request):
        uid = request.GET.get("UID")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM HSPMaterialView ORDER BY Grpid, ID")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HSPGetLogsViewSet(APIView):
    def get(self, request):
        uid = request.GET.get("UID")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spEduVideoGetLogs @User = '{uid}'")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class HSPUpdateLogViewSet(APIView):
    def post(self, request):
        rec = request.data
        try:
            uid = rec.get('UID')
            videoId = rec.get('videoId')
            comment = rec.get('comment')
            timestamp = rec.get('timestamp')
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spEduVideoUpdateLog @User = '{uid}', @VIdeoID = '{videoId}', @Comments = '{comment}', @Timestamp	= {timestamp};")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class HSPGetFavesViewSet(APIView):
    def get(self, request):
        uid = request.GET.get("UID")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spEduVideoGetFaves @User = '{uid}'")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class HSPUpdateFavesViewSet(APIView):
    def get(self, request):
        rec = request.data
        try:
            uid = rec.get('UID')
            videoId = rec.get('videoId')
            comment = rec.get('comment')
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spEduVideoUpdateFaves @User = '{uid}', @VIdeoID = '{videoId}', @Comments = '{comment}';")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         
        
class HSPGetActiveEdus(APIView):
    def get(self, request):
        try:
            uid = request.GET.get('UID')
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM NewEduWeekDetailsFunction(%s)', (uid,))
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         
        
class HSPGetMemberLoyaltyCard(APIView):
    def get(self, request):
        try:
            uid = request.GET.get('UID')
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM HSPMemberLoyaltyFunction(%s)', (uid,))
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
class HSPGetGroupAttendance(APIView):
    def get(self, request):
        rec = request.data
        try:
            uid = request.GET.get('UID')
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM NewEduGetAttendanceFunction(%s)', (uid,))
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class HSPGetMembers(APIView):
    def get(self, request):
        try:
            uid = request.GET.get('UID')
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM MembersGetGroupViewFunction(%s) ORDER BY Pos, ID', (uid,))
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HSPUpdateAttendanceViewSet(APIView):
    def post(self, request):
        rec = request.data
        try:
            uid = rec.get('UID')
            attend = rec.get('Attendance')
            eduid = rec.get('ID')
            edutype = rec.get('Type')
            reason = "'"+rec.get('Reason').replace("'","''")+"'" if rec.get('Reason') else "NULL"

            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spEduVideoUpdateAttendance @UID = '{uid}',  @Attendance = {attend}, @ID = {eduid},  @Reason ={reason},  @Type ={edutype}")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HSPExamGroupViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('uid')
        examid = request.GET.get('eid')
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""SELECT M.*, E.Score, E.Reason, E.ReportDate 
                                    FROM MembersGetGroupViewFunction('{uid}') M 
                                    LEFT JOIN (Select * From HSPExamResultsTable WHERE ExamID = {examid}) E ON E.UID = M.UID ORDER BY GID, Pos, ID
                               """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HSPExamMyGroupViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('uid')
        examid = request.GET.get('eid')
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""SELECT M.*, E.Score, E.Reason, E.ReportDate 
                                    FROM MembersGetMyGroupFunction('{uid}') M 
                                    LEFT JOIN (Select * From HSPExamResultsTable WHERE ExamID = {examid}) E ON E.UID = M.UID ORDER BY GID, Pos, ID
                               """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HSPExamUpdateScoreViewSet(APIView):
    def post(self, request):
        data = request.data
        uid = data.get('uid')
        score = data.get('score')
        examid = data.get('examid')
        reporter = data.get('reporter')
        reason = data.get('reason').replace("'","''")

        try:
            with connection.cursor() as cursor:
                
                cursor.execute(f"EXEC spHSPExamReportScore @ExamID = {examid}, @UID = '{uid}', @Score = {score}, @Reason = '{reason}', @Reporter = '{reporter}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HSPSummaryViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM HSPSummaryFunction(%s)', (uid,))
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class HSPFetchFileViewSet(APIView):
    def get(self, request):
        id = request.GET.get("FileID")
        uid = request.GET.get("UID")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spHSPEduFetchFile @UID = '{uid}',  @FileID = {id}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HSPUploadFileViewSet(APIView):
    def post(self, request):
        rec = request.data
        try:
            uid = rec.get('UID')
            fileid = rec.get('FileID')
            filename = rec.get('Filename')

            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spHSPVideoSubmit @UID = '{uid}',  @FileID = '{fileid}', @FileName = '{filename}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HSPGetSubmissionsIndViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM HSPSubmissionsIndFunction(%s) ORDER BY ID DESC', (uid,))
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HSPGetSubmissionsAllViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM HSPSubmissionsAllFunction() ORDER BY ID DESC')
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HSPUpdateCommentViewSet(APIView):
    def post(self, request):
        rec = request.data
        try:
            fileid = rec.get('FileID')
            feedback = rec.get('Feedback').replace("'","''")

            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spHSPVideoAddFeedback @FileID = '{fileid}', @Feedback = '{feedback}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HSPDropInExpDeptViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM dbo.HSPDropInExpDeptFunction() ORDER BY Division, OGID')
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HSPDropInExpIndSumViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM dbo.HSPDropInIndSumFunction()')
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HSPDeptVidSubmissionViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM [HSPDeptSubmissionSumFunction]() ORDER BY Division, Pct DESC, OGID')
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HSPGetEduWeeklySessionsViewSet(APIView):
    def get(self, request):
        print(request)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM [dbo].[HSPCurrentSessionsFunction]() ORDER BY DATE")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HSPGetEduSessionScoresViewSet(APIView):
    def get(self, request):
        print(request)
        try:
            uid = request.GET.get('UID')
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM dbo.HSPFilteredScoresFunction(%s) ORDER BY CurrentScore DESC, GID', (uid,))
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class HSPGetMWScoresViewSet(APIView):
    def get(self, request):
        print(request)
        try:
            uid = request.GET.get('UID')
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM [dbo].[HSPMWCurrentScoresFunction]() ORDER By GID')
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class HSPGetTraineeScheduleViewSet(APIView):
    def get(self, request):
        grpid = request.GET.get("GroupID")
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM dbo.HSPTraineeSessionFunction(%s)', (grpid,))
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        


# THROW numbers raised by spHSPGetLoyaltyPoints / spHSPSetLoyaltyClaimed.
# The SQL Server message reads "...[SQL Server]Not authorised ... (50403) (SQLExecDirectW)".
LOYALTY_SQL_ERRORS = {
    '50403': status.HTTP_403_FORBIDDEN,
    '50404': status.HTTP_404_NOT_FOUND,
    '50400': status.HTTP_400_BAD_REQUEST,
}


def loyalty_error(e):
    msg = str(e)
    for num, code in LOYALTY_SQL_ERRORS.items():
        if '(' + num + ')' in msg:
            return Response({'error': msg.split(']')[-1].split('(')[0].strip()}, status=code)
    return Response({'error': msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HSPLoyaltySetClaimedViewSet(APIView):
    def post(self, request):
        rec = request.data
        try:
            claimed = int(rec.get('Claimed'))
        except (TypeError, ValueError):
            return Response({'error': 'Claimed must be a whole number'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connection.cursor() as cursor:
                cursor.execute('EXEC dbo.spHSPSetLoyaltyClaimed @ActorUID = %s, @UID = %s, @Claimed = %s',
                               (rec.get('ActorUID'), rec.get('UID'), claimed))
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return loyalty_error(e)


class HSPLoyaltyRefreshViewSet(APIView):
    def post(self, request):
        key = str(request.data.get('Key') or '')
        if not hmac.compare_digest(key, settings.LOYALTY_JOB_KEY):
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        try:
            with connection.cursor() as cursor:
                cursor.execute('EXEC dbo.spHSPBulkUpdateLoyaltyPoints')

            return Response({'ok': True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# THROW numbers raised by the admin procedures in sql/HSPLoyalty.sql.
# The SQL Server message reads "...[SQL Server]Not authorised ... (50403) (SQLExecDirectW)".
HSP_ADMIN_SQL_ERRORS = {
    '50403': status.HTTP_403_FORBIDDEN,
    '50404': status.HTTP_404_NOT_FOUND,
    '50400': status.HTTP_400_BAD_REQUEST,
}


def hsp_admin_proc(sql, params):
    """Runs one admin procedure and returns its rows, or its THROW as a 4xx."""
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()] if cursor.description else []

        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        msg = str(e)
        for num, code in HSP_ADMIN_SQL_ERRORS.items():
            if '(' + num + ')' in msg:
                return Response({'error': msg.split(']')[-1].split('(')[0].strip()}, status=code)
        return Response({'error': msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def as_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class HSPLoyaltyAdminListViewSet(APIView):
    def get(self, request):
        return hsp_admin_proc('EXEC dbo.spHSPGetLoyaltyPoints @ActorUID = %s',
                              (request.GET.get('ActorUID'),))


class HSPLoyaltySetRewardsViewSet(APIView):
    def post(self, request):
        rec = request.data
        return hsp_admin_proc('EXEC dbo.spHSPSetLoyaltyRewards @ActorUID = %s, @UID = %s, @RewardIDs = %s',
                              (rec.get('ActorUID'), rec.get('UID'), str(rec.get('RewardIDs') or '')))


class HSPMemberLessonDetailViewSet(APIView):
    def get(self, request):
        grpid = as_int(request.GET.get('GrpID'))
        if grpid is None:
            return Response({'error': 'GrpID must be a number'}, status=status.HTTP_400_BAD_REQUEST)
        return hsp_admin_proc('EXEC dbo.spHSPGetMemberLessonDetail @ActorUID = %s, @UID = %s, @GrpID = %s',
                              (request.GET.get('ActorUID'), request.GET.get('UID'), grpid))


class HSPAdminSetAttendanceViewSet(APIView):
    def post(self, request):
        rec = request.data
        grpid, eduid, actid = as_int(rec.get('GrpID')), as_int(rec.get('ID')), as_int(rec.get('ActID'))
        if None in (grpid, eduid, actid) or rec.get('Cat') not in ('SVC', 'EDU'):
            return Response({'error': 'GrpID, ID, ActID and Cat are required'}, status=status.HTTP_400_BAD_REQUEST)
        return hsp_admin_proc('EXEC dbo.spHSPAdminSetAttendance @ActorUID = %s, @UID = %s, @GrpID = %s, @Cat = %s, @ID = %s, @ActID = %s',
                              (rec.get('ActorUID'), rec.get('UID'), grpid, rec.get('Cat'), eduid, actid))


class HSPExemptListViewSet(APIView):
    def get(self, request):
        return hsp_admin_proc('EXEC dbo.spHSPGetExemptMembers @ActorUID = %s',
                              (request.GET.get('ActorUID'),))


class HSPSetExemptViewSet(APIView):
    def post(self, request):
        rec = request.data
        return hsp_admin_proc('EXEC dbo.spHSPSetExempt @ActorUID = %s, @UID = %s, @Exempt = %s, @Reason = %s',
                              (rec.get('ActorUID'), rec.get('UID'), 1 if rec.get('Exempt') else 0, rec.get('Reason') or ''))



def as_date(value):
    """'YYYY-MM-DD' → date, anything else → None."""
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None
    
def as_datetime(value):
    """'YYYY-MM-DDTHH:MM[:SS]' (local, no zone) → naive datetime, else None."""
    try:
        return datetime.fromisoformat(str(value)[:19])
    except (TypeError, ValueError):
        return None


class HSPEduAdminMaterialsViewSet(APIView):
    def get(self, request):
        return hsp_admin_proc('EXEC dbo.spHSPEduAdminGetMaterials @ActorUID = %s',
                              (request.GET.get('ActorUID'),))


class HSPEduAdminGroupsViewSet(APIView):
    def get(self, request):
        return hsp_admin_proc('EXEC dbo.spHSPEduAdminGetGroups @ActorUID = %s',
                              (request.GET.get('ActorUID'),))


class HSPEduAdminSaveMaterialViewSet(APIView):
    """ID empty → add a new material; otherwise edit that one."""
    def post(self, request):
        rec = request.data
        raw_id = rec.get('ID')
        mid = None if raw_id in (None, '') else as_int(raw_id)
        mode = rec.get('GrpMode')
        grpid = as_int(rec.get('GrpID'))
        raw_lu = rec.get('LastUpdate')
        last_update = None if raw_lu in (None, '') else as_datetime(raw_lu)
        bad_id = raw_id not in (None, '') and mid is None
        bad_lu = raw_lu not in (None, '') and last_update is None
        if bad_id or bad_lu or mode not in ('auto', 'set', 'none') or (mode == 'set' and grpid is None):
            return Response({'error': 'GrpMode, (for set) GrpID and a valid LastUpdate are required'},
                            status=status.HTTP_400_BAD_REQUEST)
        return hsp_admin_proc(
            'EXEC dbo.spHSPEduAdminSaveMaterial @ActorUID = %s, @ID = %s, @Name = %s, @LinkID = %s, @Type = %s, '
            '@Category = %s, @Active = %s, @GrpMode = %s, @GrpID = %s, @LastUpdate = %s',
            (rec.get('ActorUID'), mid, rec.get('Name') or '', rec.get('LinkID') or '', rec.get('Type') or '',
             rec.get('Category') or '', 1 if rec.get('Active') else 0, mode,
             grpid if mode == 'set' else None, last_update))



class HSPEduAdminSaveGroupViewSet(APIView):
    def post(self, request):
        rec = request.data
        gid = rec.get('ID')
        gid = None if gid in (None, '') else as_int(gid)
        start, end = as_date(rec.get('StartDate')), as_date(rec.get('EndDate'))
        if (rec.get('ID') not in (None, '') and gid is None) or start is None or end is None:
            return Response({'error': 'Valid StartDate and EndDate are required'}, status=status.HTTP_400_BAD_REQUEST)
        return hsp_admin_proc(
            'EXEC dbo.spHSPEduAdminSaveGroup @ActorUID = %s, @ID = %s, @StartDate = %s, @EndDate = %s, '
            '@GroupName = %s, @Lesson = %s, @Stage = %s',
            (rec.get('ActorUID'), gid, start, end,
             rec.get('GroupName') or '', rec.get('Lesson') or '', rec.get('Stage') or ''))


# -----------------------------------------------------------------------------
# 2. urls.py
#
#    path('hspEduAdminMaterials/',    views.HSPEduAdminMaterialsViewSet.as_view()),
#    path('hspEduAdminGroups/',       views.HSPEduAdminGroupsViewSet.as_view()),
#    path('hspEduAdminSaveMaterial/', views.HSPEduAdminSaveMaterialViewSet.as_view()),
#    path('hspEduAdminSaveGroup/',    views.HSPEduAdminSaveGroupViewSet.as_view()),
# -----------------------------------------------------------------------------


# Exam scores reuse the existing hspExamUpdateScore/ (HSPExamUpdateScoreViewSet
# → spHSPExamReportScore), so there's no new view for them.


# -----------------------------------------------------------------------------
# 2. urls.py — replace hspLoyaltySetClaimed/ if you already added it
#
#    path('hspLoyaltyAdminList/',     views.HSPLoyaltyAdminListViewSet.as_view()),
#    path('hspLoyaltySetRewards/',    views.HSPLoyaltySetRewardsViewSet.as_view()),
#    path('hspMemberLessonDetail/',   views.HSPMemberLessonDetailViewSet.as_view()),
#    path('hspAdminSetAttendance/',   views.HSPAdminSetAttendanceViewSet.as_view()),
#    path('hspExemptList/',           views.HSPExemptListViewSet.as_view()),
#    path('hspSetExempt/',            views.HSPSetExemptViewSet.as_view()),
# -----------------------------------------------------------------------------
