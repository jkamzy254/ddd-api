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
                cursor.execute(f"EXEC spEVAppsScriptLogin @Username = '{username}', @Password = '{password}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            if len(result) == 0:
                return Response({'error': 'Unauthorized Access'}, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class FMPCheckFruitHistoryViewSet(APIView):
    def get(self, request):
        user = request.GET.get('User')
        phone = request.GET.get('Phone')
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spFMPGetFruitHistory @User = '{user}', @Phone = '{phone}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class FMPUnlockFruitViewSet(APIView):
    def post(self, request):
        user = request.GET.get('User')
        uid = request.GET.get('UID')
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spEVUnlockFruit @User = '{user}', @UID = '{uid}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class FMPGetMeetingsViewSet(APIView):
    def post(self, request):
        user = request.GET.get('User')
        uid = request.GET.get('UID')
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spEVGetMeetings @User = '{user}', @UID = '{uid}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        
class FMPDeleteMeetingViewSet(APIView):
    def post(self, request):
        user = request.GET.get('User')
        meetingKey = request.GET.get('MeetingKey')
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spEVDeleteMeeting @User = '{user}', @UID = '{meetingKey}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class FMPUpdateMeetingViewSet(APIView):
    def post(self, request):
        rec = request.data
        try:
            user = request.GET.get('User')
            meetingKey = request.GET.get('MeetingKey')
            attendee1 = request.GET.get('Attendee1')
            attendee2 = rec.get('Attendee2') if rec.get('Attendee2') else "NULL"
            meetdate = request.GET.get('MeetDate')
            metpicker = request.GET.get('MetPicker')
            bbtid = rec.get('BBTID') if rec.get('BBTID') else "NULL"
            outcome = request.GET.get('Outcome') if rec.get('Outcome') else "NULL"
            with connection.cursor() as cursor:
                cursor.execute(f"""EXEC spEVUpdateMeeting 
                                    @User = '{user}', @MeetingKey = '{meetingKey}',
                                    @Attendee1 = {attendee1}, @Attendee2 = {attendee2}, 
                                    @MeetDate = {meetdate}, @MetPicker = {metpicker}, 
                                    @BBTID = {bbtid}, @Outcome = {outcome};
                                    """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
        
class FMPExtendLockViewSet(APIView):
    def post(self, request):
        user = request.GET.get('User')
        uid = request.GET.get('UID')
        date = request.GET.get('Date')
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC spManualExtendFruitLock @User = '{user}', @UID = '{uid}', @Date = '{date}'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)