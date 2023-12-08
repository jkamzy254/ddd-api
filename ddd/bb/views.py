from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from api.filters import MemberFilter, BBDataFilter, SeasonFilter, ReportFilter
# from .serializers import MemberSerializer, EvseasonSerializer, BBDataSerializer, ReportSerializer,BBGroupSerializer
from ddd.models import Memberdata, Evseason, Bbdata, Report
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.db import connection
import jwt, datetime, json
from api.redis import Redis

# Create your views here.


class BBStatusGrpPerBBTViewSet(APIView):
    def get(self, request):

        try:
            payload = decode_jwt(request)
            userID = payload['UID']
            #user = Memberdata.objects.filter(id = payload['ID']).first()
            with connection.cursor() as cursor:
                cursor.execute('EXEC spBBGroupViewGetPerBBT %s', (payload['UID'],))
                bbrecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(bbrecs, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BBStatusGrpPerLeafViewSet(APIView):
    def get(self, request):

        try:
            payload = decode_jwt(request)

            with connection.cursor() as cursor:
                cursor.execute('EXEC spBBGroupViewGetPerLeaves %s', (payload['UID'],))
                bbrecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                Redis.hset('my_fruits', userID, json.dumps(bbrecs, separators=(',', ':')))
            return Response(bbrecs, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BBGetUserStudentsViewSet(APIView):
    def get(self, request):

        try:
            payload = decode_jwt(request)

            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT F.UID, MB.PREFERRED_NAME AS BBT, MB.UID 'BBTID', M1.PREFERRED_NAME AS L1, F.L1_ID, M2.PREFERRED_NAME AS L2, F.L2_ID, F.FishName, F.FishUser, F.FishPhone, F.EVPlatform, B.Label
                                FROM BBData AS B
                                LEFT JOIN MemberData AS M1 ON B.L1_ID = M1.UID
                                LEFT JOIN MemberData AS M2 ON B.L2_ID = M2.UID
                                LEFT JOIN MemberData AS MB ON B.BBT_ID = MB.UID
                                LEFT JOIN FruitData F ON F.UID = B.UID
                                WHERE B.BBT_ID = '{0}' AND B.Completed = 0
                               """.format(payload['UID'],))
                studs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                Redis.hset('my_studs', userID, json.dumps(studs, separators=(',', ':')))
            return Response(studs, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BBGetYouthBBViewSet(APIView):
    def get(self, request):

        try:
            payload = decode_jwt(request)
            with connection.cursor() as cursor:
                cursor.execute("EXEC spGetYouthActiveBB")
                bbs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(bbs, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BBGetMEViewSet(APIView):
    def get(self, request):
        me_cursor = connection.cursor()
        exp_cursor = connection.cursor()
        pick_cursor = connection.cursor()
        expmeet_cursor = connection.cursor()
        exppick_cursor = connection.cursor()

        try:
            payload = decode_jwt(request)

            me_cursor.execute("""
                            SELECT B.UID, FruitName, LastUpdate, (SELECT Short FROM BBTopicData WHERE ID = B.LastTopic) 'Last_Topic'
                            FROM BBData B
                            LEFT JOIN MissEduData M ON M.UID = B.UID
                            WHERE BBT_ID = '{0}' AND Completed = 0 AND Status = 'Missed Education'
                            AND (CAST(M.ReportDate AS DATE) IS NULL OR CAST(M.ReportDate AS DATE) < CAST(B.NextClassDate AS DATE))
                            """.format(payload['UID'],))
            me_recs = [dict(zip([column[0] for column in me_cursor.description], record)) for record in me_cursor.fetchall()]
            exp_cursor.execute("""
                            SELECT UID, FruitName, LastUpdate, (SELECT Short FROM BBTopicData WHERE ID = B.LastTopic) 'Last_Topic'
                            FROM BBData B
                            WHERE BBT_ID = '{0}'
                            AND Completed = 0
                            AND CAST(NextClassDate AS DATE) = CAST((SELECT SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time') AS DATE)
                            AND Status != 'Missed Education';
                            """.format(payload['UID'],))
            exp_recs = [dict(zip([column[0] for column in exp_cursor.description], record)) for record in exp_cursor.fetchall()]
            pick_cursor.execute("EXEC spStudentList_GetPPList '{0}'".format(payload['UID'],))
            pick_recs = [ dict( zip( [column[0] for column in pick_cursor.description] , record ) ) for record in pick_cursor.fetchall()]
            expmeet_cursor.execute("EXEC spFMPGetExpMeet '{0}'".format(payload['UID'],))
            expmeet_recs = [ dict( zip( [column[0] for column in expmeet_cursor.description] , record ) ) for record in expmeet_cursor.fetchall()]
            exppick_cursor.execute("EXEC spFMPGetExpPick '{0}'".format(payload['UID'],))
            exppick_recs = [ dict( zip( [column[0] for column in exppick_cursor.description] , record ) ) for record in exppick_cursor.fetchall()]

            data = {
                "ME": {"records": me_recs, "number": len(me_recs)},
                "Expected": {"records": exp_recs, "number": len(exp_recs)},
                "PickConfirm": {"records": pick_recs, "number": len(pick_recs)},
                "ExpMeet": {"records": expmeet_recs},
                "ExpPick": {"records": exppick_recs}
            }

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    # pagination_class = PageNumberPagination
