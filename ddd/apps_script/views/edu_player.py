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
                cursor.execute(f"""
                Select M.UID, PREFERRED_NAME as 'Name', (SELECT T.TID, T.PID FROM TGWPositionLog T WHERE T.UID = M.UID And EndDate IS NULL FOR JSON PATH) AS Positions
                FROM MemberData M Where Username = '{username}' And Password = '{password}';
                """)
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