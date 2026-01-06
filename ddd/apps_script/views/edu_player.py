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
                cursor.execute("SELECT * FROM NewEduASLoginFunction(%s, %s)", [username,password])
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            if len(result) == 0:
                return Response({'error': 'Unauthorized Access'}, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class EduVideoGetFoldersViewSet(APIView):
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
        

class EduVideoGetMaterialViewSet(APIView):
    def get(self, request):
        uid = request.GET.get("UID")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM NewEduMaterialTable")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EduVideoGetLogsViewSet(APIView):
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
        

class EduVideoUpdateLogViewSet(APIView):
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
    

class EduVideoGetFavesViewSet(APIView):
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
        

class EduVideoUpdateFavesViewSet(APIView):
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
         
        
class EduVideoGetActiveEdus(APIView):
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
        
        
        
class EduVideoGetGroupAttendance(APIView):
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
        
class EduVideoGetMembers(APIView):
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
        
        
class EduVideoUpdateAttendanceViewSet(APIView):
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
        
class EduVideosExamGroupViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('uid')
        examid = request.GET.get('eid')
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""SELECT M.*, E.Score, E.Reason, E.ReportDate 
                                    FROM MembersGetGroupViewFunction('{uid}') M 
                                    LEFT JOIN (Select * From NewEduExamResultsTable WHERE ExamID = {examid}) E ON E.UID = M.UID ORDER BY GID, Pos, ID
                               """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class EduVideosExamMyGroupViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('uid')
        examid = request.GET.get('eid')
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""SELECT M.*, E.Score, E.Reason, E.ReportDate 
                                    FROM MembersGetMyGroupFunction('{uid}') M 
                                    LEFT JOIN (Select * From NewEduExamResultsTable WHERE ExamID = {examid}) E ON E.UID = M.UID ORDER BY GID, Pos, ID
                               """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class EduVideosSummaryViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('UID')
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM NewEduSummaryFunction(%s)', (uid,))
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        