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
    
        
class CTUpdateStudentStatusViewSet(APIView):
    def post(self, request):
        rec = request.data
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""EXEC spCTUpdateStudentStatus
                    @UID = '{rec.get('UID')}', @Registration = {rec.get('Registration')}, @Status = {rec.get('Status')}, @StudName = '{rec.get('StudName').replace("'","''")}'
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
        bltDone = data.get('BLTDone')
        bltJDSN =   data.get('BLTJDSN')
        hmrmJDSN = data.get('HmrmJDSN')
        intDone = data.get('IntDone')
        intDT = data.get('IntDT')
        reaction = data.get('Reaction')

        try:
            with connection.cursor() as cursor:
                
                cursor.execute(f"""EXEC spBBUpdateTransitionCT 
                                    @UID = {uid}, 
                                    @TextBBT = '{textBBT}', 
                                    @BLTDone = {bltDone}, 
                                    @BLTJDSN = {bltJDSN}, 
                                    @HmrmJDSN = {hmrmJDSN}, 
                                    @IntDone = {intDone}, 
                                    @IntDT = {intDT}, 
                                    @Reaction = {reaction}
                               """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        