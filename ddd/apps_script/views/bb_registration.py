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
                cursor.execute(f"""Select UID, PREFERRED_NAME as 'Name' From MemberData 
                               Where BBT = 1 And Username = '{username}' And Password = '{password}' AND UID IN (Select BBT_ID From PrevSsnStudentsView)""")
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
        
class GetSuburbsViewSet(APIView):
    def get(self, request):
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("Select * From SuburbTable")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ReportStudentViewSet(APIView):
    def post(self, request):
        data = request.data
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""EXEC spBBReportStudRegistration 
                                    @UID = '{data['uid']}', 
                                    @Fname = '{data['fname'].replace("'", "''")}', 
                                    @Mname = '{data['mname'].replace("'", "''")}', 
                                    @Lname = '{data['lname'].replace("'", "''")}', 
                                    @Suburb = '{data['suburb'].replace("'", "''")}', 
                                    @English = {data['english']}, 
                                    @DoB = {data['dob']}, 
                                    @Gender = {data['gender']}, 
                                    @Church = {data['church'].replace("'", "''")}, 
                                    @Period = {data['period']}, 
                                    @CtCheck = {data['ctcheck']}, 
                                    @PrevCT = {data['prevct'].replace("'", "''")}
                               """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

