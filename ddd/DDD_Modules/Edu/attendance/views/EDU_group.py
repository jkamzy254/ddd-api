from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection

       
class EDUGetGroupWeeklylogViewSet(APIView):
    def get(self, request):
        
        try:
            token = decode_jwt(request)   
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM EducationLogMemberList('{token['UID']}')")
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(recs, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class EDUUpdateAttendanceViewSet(APIView):
    def post(self, request):

        try:   
            token = decode_jwt(request)  
            payload = request.data
            rsn = payload['reason'].replace("'", "''") if payload['reason'] is not None else None
            reason_value = f"'{rsn}'" if payload['reason'] is not None else "NULL"
            with connection.cursor() as cursor:
                if payload['ea'] == 'E':
                    cursor.execute(f"""EXEC sp_Education_UpdateExpectedAttendance 
                        @uid = {payload['uid']}, 
                        @eid = {payload['eid']}, 
                        @esid = {payload['esid']}, 
                        @reason = {reason_value}
                    """)
                    res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                elif payload['ea'] == 'A':
                    cursor.execute(f"""EXEC sp_Education_UpdateActualAttendance 
                        @uid = {payload['uid']}, 
                        @eid = {payload['eid']}, 
                        @esid = {payload['esid']}, 
                        @reason = {reason_value}
                    """)
                    res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class EDUGetWeekBreakdown(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            payload = request.data
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC sp_Education_GetWeekBreakdown('{token['UID']}')")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
        
class EDUGetActiveEducations(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM Education_GetEducations")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
        
class EDUGetGroupAttendance(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM Education_GroupAttendance('{token['UID']}',{request.GET.get('eid')})")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)