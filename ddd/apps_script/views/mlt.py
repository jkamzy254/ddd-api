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


        
class MLTGetMemberViewSet(APIView):
    def get(self, request):
        username = request.GET.get('username')
        password = request.GET.get('password')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM MLTLoginFunction(%s, %s)", [username,password])
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            if len(result) == 0:
                return Response({'error': 'Unauthorized Access'}, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

class MLTGetMaterialViewSet(APIView):
    def get(self, request):
        uid = request.GET.get("UID")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM MLTMaterialTable")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
class MLTFetchFileViewSet(APIView):
    def get(self, request):
        id = request.GET.get("FileID")
        uid = request.GET.get("UID")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spMLTFetchFile @UID = '{uid}',  @FileID = {id}")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class HSPGetLogsViewSet(APIView):
#     def get(self, request):
#         uid = request.GET.get("UID")
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute(f"EXEC spEduVideoGetLogs @User = '{uid}'")
#                 res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
#             return Response(res, status=status.HTTP_200_OK)
#         except Exception as e:
#             # Handle exceptions here, e.g., logging or returning an error response
#             print(e)
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# class HSPUpdateLogViewSet(APIView):
#     def post(self, request):
#         rec = request.data
#         try:
#             uid = rec.get('UID')
#             videoId = rec.get('videoId')
#             comment = rec.get('comment')
#             timestamp = rec.get('timestamp')
#             with connection.cursor() as cursor:
#                 cursor.execute(f"EXEC spEduVideoUpdateLog @User = '{uid}', @VIdeoID = '{videoId}', @Comments = '{comment}', @Timestamp	= {timestamp};")
#                 res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
#             return Response(res, status=status.HTTP_200_OK)
#         except Exception as e:
#             # Handle exceptions here, e.g., logging or returning an error response
#             print(e)
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        

# class HSPUpdateFavesViewSet(APIView):
#     def get(self, request):
#         rec = request.data
#         try:
#             uid = rec.get('UID')
#             videoId = rec.get('videoId')
#             comment = rec.get('comment')
#             with connection.cursor() as cursor:
#                 cursor.execute(f"EXEC spEduVideoUpdateFaves @User = '{uid}', @VIdeoID = '{videoId}', @Comments = '{comment}';")
#                 res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
#             return Response(res, status=status.HTTP_200_OK)
#         except Exception as e:
#             # Handle exceptions here, e.g., logging or returning an error response
#             print(e)
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
        
        
# class HSPGetGroupAttendance(APIView):
#     def get(self, request):
#         rec = request.data
#         try:
#             uid = request.GET.get('UID')
#             with connection.cursor() as cursor:
#                 cursor.execute('SELECT * FROM NewEduGetAttendanceFunction(%s)', (uid,))
#                 res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
#             return Response(res, status=status.HTTP_200_OK)
#         except Exception as e:
#             # Handle exceptions here, e.g., logging or returning an error response
#             print(e)
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# class HSPUpdateAttendanceViewSet(APIView):
#     def post(self, request):
#         rec = request.data
#         try:
#             uid = rec.get('UID')
#             attend = rec.get('Attendance')
#             eduid = rec.get('ID')
#             edutype = rec.get('Type')
#             reason = "'"+rec.get('Reason').replace("'","''")+"'" if rec.get('Reason') else "NULL"

#             with connection.cursor() as cursor:
#                 cursor.execute(f"EXEC spEduVideoUpdateAttendance @UID = '{uid}',  @Attendance = {attend}, @ID = {eduid},  @Reason ={reason},  @Type ={edutype}")
#                 result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]

#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# class HSPExamGroupViewSet(APIView):
#     def get(self, request):
#         uid = request.GET.get('uid')
#         examid = request.GET.get('eid')
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute(f"""SELECT M.*, E.Score, E.Reason, E.ReportDate 
#                                     FROM MembersGetGroupViewFunction('{uid}') M 
#                                     LEFT JOIN (Select * From HSPExamResultsTable WHERE ExamID = {examid}) E ON E.UID = M.UID ORDER BY GID, Pos, ID
#                                """)
#                 result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# class HSPExamMyGroupViewSet(APIView):
#     def get(self, request):
#         uid = request.GET.get('uid')
#         examid = request.GET.get('eid')
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute(f"""SELECT M.*, E.Score, E.Reason, E.ReportDate 
#                                     FROM MembersGetMyGroupFunction('{uid}') M 
#                                     LEFT JOIN (Select * From HSPExamResultsTable WHERE ExamID = {examid}) E ON E.UID = M.UID ORDER BY GID, Pos, ID
#                                """)
#                 result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# class HSPExamUpdateScoreViewSet(APIView):
#     def post(self, request):
#         data = request.data
#         uid = data.get('uid')
#         score = data.get('score')
#         examid = data.get('examid')
#         reporter = data.get('reporter')
#         reason = data.get('reason').replace("'","''")

#         try:
#             with connection.cursor() as cursor:
                
#                 cursor.execute(f"EXEC spHSPExamReportScore @ExamID = {examid}, @UID = '{uid}', @Score = {score}, @Reason = '{reason}', @Reporter = '{reporter}'")
#                 result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# class HSPSummaryViewSet(APIView):
#     def get(self, request):
#         uid = request.GET.get('UID')
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute('SELECT * FROM HSPSummaryFunction(%s)', (uid,))
#                 result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]

#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# class HSPUploadFileViewSet(APIView):
#     def post(self, request):
#         rec = request.data
#         try:
#             uid = rec.get('UID')
#             fileid = rec.get('FileID')
#             filename = rec.get('Filename')

#             with connection.cursor() as cursor:
#                 cursor.execute(f"EXEC spHSPVideoSubmit @UID = '{uid}',  @FileID = '{fileid}', @FileName = '{filename}'")
#                 result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]

#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# class HSPGetSubmissionsIndViewSet(APIView):
#     def get(self, request):
#         uid = request.GET.get('UID')
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute('SELECT * FROM HSPSubmissionsIndFunction(%s) ORDER BY ID DESC', (uid,))
#                 result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# class HSPGetSubmissionsAllViewSet(APIView):
#     def get(self, request):
#         uid = request.GET.get('UID')
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute('SELECT * FROM HSPSubmissionsAllFunction() ORDER BY ID DESC')
#                 result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# class HSPUpdateCommentViewSet(APIView):
#     def post(self, request):
#         rec = request.data
#         try:
#             fileid = rec.get('FileID')
#             feedback = rec.get('Feedback').replace("'","''")

#             with connection.cursor() as cursor:
#                 cursor.execute(f"EXEC spHSPVideoAddFeedback @FileID = '{fileid}', @Feedback = '{feedback}'")
#                 result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]

#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# class HSPDropInExpDeptViewSet(APIView):
#     def get(self, request):
#         uid = request.GET.get('UID')
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute('SELECT * FROM dbo.HSPDropInExpDeptFunction() ORDER BY Division, OGID')
#                 result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# class HSPDropInExpIndSumViewSet(APIView):
#     def get(self, request):
#         uid = request.GET.get('UID')
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute('SELECT * FROM dbo.HSPDropInIndSumFunction()')
#                 result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# class HSPDeptVidSubmissionViewSet(APIView):
#     def get(self, request):
#         uid = request.GET.get('UID')
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute('SELECT * FROM [HSPDeptSubmissionSumFunction]() ORDER BY Division, Pct DESC, OGID')
#                 result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# class HSPGetEduWeeklySessionsViewSet(APIView):
#     def get(self, request):
#         print(request)
#         try:
#             with connection.cursor() as cursor:
#                 cursor.execute("SELECT * FROM [dbo].[HSPCurrentSessionsFunction]() ORDER BY DATE")
#                 result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# class HSPGetEduSessionScoresViewSet(APIView):
#     def get(self, request):
#         print(request)
#         try:
#             uid = request.GET.get('UID')
#             with connection.cursor() as cursor:
#                 cursor.execute('SELECT * FROM dbo.HSPFilteredScoresFunction(%s) ORDER BY CurrentScore DESC, GID', (uid,))
#                 result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
# class HSPGetMWScoresViewSet(APIView):
#     def get(self, request):
#         print(request)
#         try:
#             uid = request.GET.get('UID')
#             with connection.cursor() as cursor:
#                 cursor.execute('SELECT * FROM [dbo].[HSPMWCurrentScoresFunction]() ORDER By GID')
#                 result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

#             return Response(result, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
     