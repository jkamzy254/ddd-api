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
                cursor.execute(f"Select UID, PREFERRED_NAME as 'Name' From MemberData Where BBT = 1 And Username = '{username}' And Password = '{password}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            if len(result) == 0:
                return Response({'error': 'Unauthorized Access'}, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetStudentsViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('uid')
        print(uid)
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"Select UID, FruitName, Stat_Abbr From PrevSsnStudentsView WHERE BBT_ID = '{uid}' And Stat_Abbr != 'FA'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ReportStudentViewSet(APIView):
    def post(self, request):
        fid = request.data['fid']
        uid = request.data['uid']
        reason = request.data['reason']
        description = request.data['description'].replace("'", "''")
        
        print(reason)
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""EXEC spBBReportFortnightFallen 
                                    @UID = '{fid}', 
                                    @Reason = '{description}', 
                                    @ReasonCategory = '{reason}', 
                                    @Reporter = '{uid}'
                               """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
