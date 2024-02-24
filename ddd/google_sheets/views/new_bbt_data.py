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
                    DECLARE @SsnStart DATE = (
                        SELECT MIN(StartDate) FROM EVSeason 
                        WHERE StartDate <= (SELECT SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time') 
                        AND ClosingDate >= (SELECT SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time')
                    );
                    SELECT M.Group_IMWY, GI.Grp, M.Name, 
                    (Select COUNT(*) From FruitData Where F_TIME >= @SsnStart And (F1_ID = M.UID Or F2_ID = M.UID)) 'FS', 
                    (Select COUNT(*) From FruitData Where M_TIME >= @SsnStart And (Attendee_1_ID = M.UID Or Attendee_2_ID = M.UID)) 'MS', 
                    (Select COUNT(*) From FruitData Where P_TIME >= @SsnStart And (L1_ID = M.UID Or L2_ID = M.UID)) 'PS',
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
        data = int(float(request.data['season']))
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
        
class GetCurrentCCTViewSet(APIView):
    def post(self, request):
        print(request.data['season'])
        data = int(float(request.data['season']))
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT M.Group_IMWY 'Dept', GI.Grp 'Group', M.Name, B.FruitName FROM BBData B
                    LEFT JOIN MemberData M ON B.BBT_ID = M.UID
                    LEFT JOIN (Select * From GroupLog Where EndDate IS NULL) G ON G.UID = M.UID
                    LEFT JOIN GroupInfo GI ON GI.GID = G.GID
                    WHERE Season = {0} AND Stat_Abbr = 'CCT'
                    ORDER By G.GID, M.Internal_Position
                """.format(data))
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetCCTInactiveViewSet(APIView):
    def post(self, request):
        print(request.data['season'])
        data = int(float(request.data['season']))
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT CONCAT(MB.Group_IMWY,' - ',CASE WHEN MB.Group_IMWY IN ('D1','D2','D3','D4','D5','D6','D7') THEN CONCAT('G',MB.MemberGroup) ELSE MB.MemberGroup END) 'BBT Grp', 
                        MB.PREFERRED_NAME 'BBT', B.FruitName 'Student', CAST(B.LastUpdate AS DATE) 'Last Class Date', B.Last_Topic 'Last Topic',
                        CONCAT('(',CASE WHEN M1.Group_IMWY IN ('D1','D2','D3','D4','D5','D6','D7') THEN CONCAT('G',M1.MemberGroup) ELSE M1.MemberGroup END, ') ', M1.PREFERRED_NAME) 'L1', 
                        CASE WHEN L2_ID IS NULL THEN '' ELSE CONCAT('(',CASE WHEN M2.Group_IMWY IN ('D1','D2','D3','D4','D5','D6','D7') THEN CONCAT('G',M2.MemberGroup) ELSE M2.MemberGroup END, ') ', M2.PREFERRED_NAME) END AS 'L2'
                    FROM BBData B 
                    LEFT JOIN CtCardData C ON B.UID = C.UID
                    LEFT JOIN MembersFull M1 ON B.L1_ID = M1.UID
                    LEFT JOIN MembersFull M2 ON B.L2_ID = M2.UID
                    LEFT JOIN MembersFull MB ON B.BBT_ID = MB.UID
                    WHERE B.Season = {0} AND B.Stat_Abbr = 'CCT' AND B.Status = 'Missed Education'
                    ORDER BY [BBT Grp]
                """.format(data))
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetPotentialBTMViewSet(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    WITH BBwithFE AS (
                        SELECT * FROM BBDataView WHERE Season = 52 AND UID IN (Select UID From Report)
                    ), MembersBB AS (
                        SELECT Group_IMWY 'Dept', GI.Grp, M.Name, (Select COUNT(*) FROM BBwithFE WHERE L1_ID = M.UID OR L2_ID = M.UID) 'CT', GL.GID 
                        FROM MemberData M 
                        LEFT JOIN (Select * FROM GroupLog WHERE EndDate IS NULL) GL ON GL.UID = M.UID
                        LEFT JOIN GroupInfo GI ON GI.GID = GL.GID
                        WHERE M.Group_IMWY IN ('D1','D2','D3','D4','D5','D6','D7','D8')
                        AND M.UID NOT IN (Select UID From BBTLog WHERE EndDate IS NULL) AND M.UID NOT IN (Select UID From CTData Where CTNum = 'SMC153')
                    )
                    SELECT Dept, Grp, Name, CT FROM MembersBB WHERE CT > 1  ORDER BY GID
                """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class GetCurrentCTBBTDataViewSet(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT B.* FROM BBTPerformanceView B
                    LEFT JOIN MemberData BBT ON BBT.UID = B.UID
                    LEFT JOIN (Select * From GroupLog Where EndDate IS NULL) GL ON GL.UID = B.UID
                    LEFT JOIN GroupInfo GI ON GL.GID = GI.GID
                    ORDER BY GI.GID, Internal_Position
                """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
              
class GetBTMListViewSet(APIView):
    def post(self, request):
        print(request.data['btm'])
        btm = request.data['btm']
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM BTMBBListFunction('{btm}')")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        
    def post(self, request):
        print(request.data['season'])
        data = int(float(request.data['season']))
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
              
class GetFebCTDataViewSet(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                        SELECT B.* FROM BBTPerformanceView B
                        LEFT JOIN MemberData BBT ON BBT.UID = B.UID
                        LEFT JOIN (Select * From GroupLog Where EndDate IS NULL) GL ON GL.UID = B.UID
                        LEFT JOIN GroupInfo GI ON GL.GID = GI.GID
                        ORDER BY GI.GID, Internal_Position
                    """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GetCurrentCTDataViewSet(APIView):
    def post(self, request):
        print(request.data['season'])
        season = request.data['season']
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM SheetBBTData({season})")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetPViewSet(APIView):
    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        bbt.Group_IMWY Dept, bbt.MemberGroup Grp, 
                        bbt.PREFERRED_NAME BBT, FishName Fruit, 
                        P_TIME PickDate, ISNULL(FE_Date,DATEADD(DAY, 6, P_TIME))FE_Deadline
                    FROM FruitData f
                    LEFT JOIN MemberData bbt ON bbt.UID = f.BBT_ID
                    LEFT JOIN ScottFEData fe ON fe.UID = f.UID
                    LEFT JOIN BBData b ON b.UID = f.UID
                    WHERE b.Season = (SELECT dbo.seasonid())
                    ORDER BY LEN(MemberGroup), Grp, BBT, P_TIME
                    """)
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetBTMFruitsViewSet(APIView):
    def post(self, request):
        btm = int(float(request.data['btm']))
        ssn = int(float(request.data['season']))
        try:
            with connection.cursor() as cursor:
                cursor.execute("spGetBTMFruits @BTM = '{0}', @SSN = {1}".format(btm, ssn))
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)