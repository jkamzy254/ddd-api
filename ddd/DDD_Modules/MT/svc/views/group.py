from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection


# Create your views here.
class SVCGetPeriodAttendanceViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            with connection.cursor() as cursor:
                cursor.execute('EXEC spSVCGetGrpPeriodAttendance %s', (payload['UID'],))
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(recs, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class SVCGetGroupWeeklylogViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            print(payload)
            with connection.cursor() as cursor:
                cursor.execute('EXEC spSVCGetGroupWeeklyLog %s', (payload['UID'],))
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(recs, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class SVCUpdateAttendanceViewSet(APIView):
    def post(self, request):
        payload = request.data
        rsn = payload['reason'].replace("'", "''") if payload['reason'] is not None else None
        reason_value = f"'{rsn}'" if payload['reason'] is not None else "NULL"

        try:   
            with connection.cursor() as cursor:
                if payload['ea'] == 'E':
                    cursor.execute(f"""EXEC sp_Service_UpdateExpectedAttendance 
                        @uid = {payload['uid']}, 
                        @sid = {payload['sid']}, 
                        @ssid = {payload['ssid']}, 
                        @reason = {reason_value}
                    """)
                    res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                elif payload['ea'] == 'A':
                    cursor.execute(f"""EXEC sp_Service_UpdateActualAttendance 
                        @uid = {payload['uid']}, 
                        @sid = {payload['sid']}, 
                        @ssid = {payload['ssid']}, 
                        @late = {payload['late']},
                        @reason = {reason_value}
                    """)
                    res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class SVCGetWeekBreakdown(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            payload = request.data
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM Service_WeekBreakdown('{token['UID']}')")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)