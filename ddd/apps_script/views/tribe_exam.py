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
                cursor.execute(f"EXEC spExamAppsScriptLogin @Username = '{username}', @Password = '{password}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            if len(result) == 0:
                return Response({'error': 'Unauthorized Access'}, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetGroupViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('uid')
        examid = request.GET.get('eid')
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""SELECT M.*, E.Score, E.Reason, E.ReportDate 
                                    FROM MembersGetGroupViewFunction('{uid}') M 
                                    LEFT JOIN (Select * From ExamResultsTable WHERE ExamID = {examid}) E ON E.UID = M.UID ORDER BY GID, Pos, ID
                               """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class GetMyGroupViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('uid')
        examid = request.GET.get('eid')
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""SELECT M.*, E.Score, E.Reason, E.ReportDate 
                                    FROM MembersGetMyGroupFunction('{uid}') M 
                                    LEFT JOIN (Select * From ExamResultsTable WHERE ExamID = {examid}) E ON E.UID = M.UID ORDER BY GID, Pos, ID
                               """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class UpdateExamScoreViewSet(APIView):
    def post(self, request):
        data = request.data
        uid = data.get('uid')
        score = data.get('score')
        examid = data.get('examid')
        reporter = data.get('reporter')
        reason = data.get('reason').replace("'","''")

        try:
            with connection.cursor() as cursor:
                
                cursor.execute(f"EXEC spExamReportScore @ExamID = {examid}, @UID = '{uid}', @Score = {score}, @Reason = '{reason}', @Reporter = '{reporter}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class UpdateExamScoreSheetsViewSet(APIView):
    def post(self, request):
        data = request.data
        evid = data.get('evid')
        score = data.get('score')
        examid = data.get('examid')
        reporter = data.get('reporter')
        reason = data.get('reason').replace("'","''")

        try:
            with connection.cursor() as cursor:
                
                cursor.execute(f"EXEC spExamReportScore @ExamID = {examid}, @EVID = '{evid}', @Score = {score}, @Reason = '{reason}', @Reporter = '{reporter}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        