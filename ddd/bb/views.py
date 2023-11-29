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
                cursor.execute('EXEC spBBGroupViewGetPerBBT %s', (userID,))
                bbrecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(bbrecs, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BBStatusGrpPerLeafViewSet(APIView):
    def get(self, request):

        try:
            payload = decode_jwt(request)
            userID = payload['UID']
            #user = Memberdata.objects.filter(id = payload['ID']).first()

            if(Redis.checkExists('my_fruits', userID)):
                print("Key exists in Redis")
                return Response(json.loads(Redis.hget('my_fruits', userID)), status=status.HTTP_200_OK)

            with connection.cursor() as cursor:
                cursor.execute('EXEC spBBGroupViewGetPerLeaves %s', (userID,))
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
            userID = payload['UID']
            #user = Memberdata.objects.filter(id = payload['ID']).first()

            if(Redis.checkExists('my_studs', userID)):
                print("Key exists in Redis")
                return Response(json.loads(Redis.hget('my_studs', userID)), status=status.HTTP_200_OK)

            with connection.cursor() as cursor:
                cursor.execute(f"""
                               SELECT F.UID, MB.PREFERRED_NAME AS BBT, MB.UID 'BBTID', M1.PREFERRED_NAME AS L1, F.L1_ID, M2.PREFERRED_NAME AS L2, F.L2_ID, F.FishName, F.FishUser, F.FishPhone, F.EVPlatform, B.Label
                                FROM BBData AS B
                                LEFT JOIN MemberData AS M1 ON B.L1_ID = M1.UID
                                LEFT JOIN MemberData AS M2 ON B.L2_ID = M2.UID
                                LEFT JOIN MemberData AS MB ON B.BBT_ID = MB.UID
                                LEFT JOIN FruitData F ON F.UID = B.UID
                                WHERE B.BBT_ID = '{userID}' AND B.Completed = 0
                               """)
                studs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                Redis.hset('my_studs', userID, json.dumps(studs, separators=(',', ':')))
            return Response(studs, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    # pagination_class = PageNumberPagination
