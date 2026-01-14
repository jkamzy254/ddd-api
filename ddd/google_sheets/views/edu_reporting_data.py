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


class GetEduWeeklyAttendanceViewSet(APIView):
    def get(self, request):
        print(request)
        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spEducation_GetDeptWeekBreakdown")
                bbrecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(bbrecs, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetEduWeeklySessionsViewSet(APIView):
    def get(self, request):
        print(request)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT Type, Date FROM Education_GetEducations UNION SELECT Type, Date FROM Service_GetServices WHERE Type = 'Wed'")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        