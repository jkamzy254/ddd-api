from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection

import json

# Create your views here.


class GetBBViewSet(APIView):
    def get(self, request):
        print(request)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM ScottBBList('%','%')")
                bbrecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(bbrecs, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetBTMFMPViewSet(APIView):
    def get(self, request):
        print(request)
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    DECLARE @CurrDate DATE = CAST((SELECT SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time') AS DATE);
                    DECLARE @Date DATE = CASE
                    WHEN DATEPART(WEEKDAY, @CurrDate) BETWEEN 2 AND 4 THEN (SELECT DATEADD(wk, DATEDIFF(wk,0,@CurrDate)-1, 3))
                    ELSE (SELECT DATEADD(wk, DATEDIFF(wk,0,@CurrDate), 3))
                    END;
                    SELECT M.Group_IMWY, GI.Grp, M.Name, 
                    (Select COUNT(*) From FruitData Where F_TIME > '2023-11-29' And (F1_ID = M.UID Or F2_ID = M.UID)) 'FS', 
                    (Select COUNT(*) From FruitData Where M_TIME > '2023-11-29' And (Attendee_1_ID = M.UID Or Attendee_2_ID = M.UID)) 'MS', 
                    (Select COUNT(*) From FruitData Where P_TIME > '2023-11-29' And (L1_ID = M.UID Or L2_ID = M.UID)) 'PS',
                    (Select COUNT(*) From FruitData Where F_TIME > @Date And (F1_ID = M.UID Or F2_ID = M.UID)) 'FW', 
                    (Select COUNT(*) From FruitData Where M_TIME > @Date And (Attendee_1_ID = M.UID Or Attendee_2_ID = M.UID)) 'MW', 
                    (Select COUNT(*) From FruitData Where P_TIME > @Date And (L1_ID = M.UID Or L2_ID = M.UID)) 'PW'
                    FROM MemberData M 
                    LEFT JOIN (Select * From GroupLog Where EndDate IS NULL) G ON G.UID = M.UID
                    LEFT JOIN GroupInfo GI ON GI.GID = G.GID
                    WHERE ID IN 
                    (   
                        334, 599, 936, 337, 536, 938, 712, 655, 283, 350, 905, 423, 
                        291, 569, 575, 256, 886, 171, 612, 1027, 1028, 1013, 1050, 
                        1076, 1054, 1046, 1021, 1024, 1049, 1017, 1015, 983, 
                        436, 456, 985, 1022, 540, 999, 547
                    )
                    ORDER By G.GID, M.Internal_Position            
                """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetBBTDataViewSet(APIView):
    def get(self, request):
        print(request)
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT UID, ID,
                    CASE 
                            WHEN Grp = 'Department' THEN 'Office'
                            ELSE Dept
                    END AS Dept,
                    CASE 
                            WHEN Grp = 'Department' THEN 'OFFC'
                            WHEN Grp = 'Serving' THEN 'SV'
                            WHEN Grp = 'Culture' THEN 'CULT'
                            ELSE Grp
                    END AS Grp,
                    BBT, P, Act, CCT, INACT, Total
                    FROM ScottBBTData((SELECT dbo.seasonid()), 'Active','%')
                    WHERE LEN(Grp) < 3 OR Grp IN ('HWPL','Culture','Serving','Department')
                    ORDER BY LEN(Grp), Grp
                """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetBBNotFallenViewSet(APIView):
    def post(self, request):
        print(request.data['season'])
        data = int(request.data['season'])
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT M.Group_IMWY 'Dept', GI.Grp 'Group', M.Name, B.FruitName FROM BBData B
                    LEFT JOIN MemberData M ON B.BBT_ID = M.UID
                    LEFT JOIN (Select * From GroupLog Where EndDate IS NULL) G ON G.UID = M.UID
                    LEFT JOIN GroupInfo GI ON GI.GID = G.GID
                    WHERE Season = {0} AND Stat_Abbr NOT IN ('CCT','FA')
                    ORDER By G.GID, M.Internal_Position
                """.format(data))
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
