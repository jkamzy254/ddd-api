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


        
class CTGetAttendanceSummaryViewSet(APIView):
    def get(self, request):
        ctid = request.GET.get("CTID")
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    SELECT *, 
                    (Select Count(*) From CTScheduleLogTable WHERE CTID = C.CTID) 'CTClasses', 
                    (Select Count(*) From CTAttendanceTable CA LEFT JOIN CTScheduleLogTable CS ON CS.ID = CA.CTDayID WHERE CTID = C.CTID AND UID = C.UID) 'StudAttendance'
                    FROM CTStudentTable C WHERE CTID = {ctid}
                """)
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
                for rec in data:
                    cursor.execute(f"""EXEC spCTUpdateSchedule 
                        @CTID = {rec.get('CTID')}, @Date = {rec.get('Date')}, @Topic = {rec.get('Topic')}
                    """)
                result = f"Update for CT Day {data[0]['Date']} done"

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
                result = f"Update for CT Day {rec['Date']} done"

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        
class CTUpdateStudentStatusViewSet(APIView):
    def post(self, request):
        rec = request.data
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""EXEC spCTUpdateStudentStatus
                    @UID = '{rec.get('UID')}', @Registration = {rec.get('Registration')}, @Status = {rec.get('Status')}
                """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()][0]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
