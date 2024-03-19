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
        
class GetBBStatsViewSet(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                      SELECT DISTINCT CTNum, (
                        SELECT COUNT(*) FROM BBDATA 
                        WHERE (
                        L1_ID IN (SELECT UID FROM CTData WHERE CTNum = C.CTNum) 
                        OR 
                        L2_ID IN (SELECT UID FROM CTData WHERE CTNum = C.CTNum) 
                        ) AND Season >= (
                            SELECT MIN(ID) FROM EVSeason 
                            WHERE StartDate < (SELECT SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time') 
                            AND EndDate > (SELECT SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')
                        ) 
                        AND Stat_Abbr != 'FA'
                        AND UID IN (Select UID FROM Report)
                    ) 'BBs'
                    FROM CTData C WHERE CTNum >= 'CT152' AND CTNum NOT LIKE '%NF%'
                    ORDER BY CTNum
                """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
