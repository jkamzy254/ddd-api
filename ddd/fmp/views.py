from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from ddd.models import Memberdata, Evseason, Report
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
import jwt, datetime
import json

# Create your views here.

class FMPStatusGrpViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            user = payload['user']
            with connection.cursor() as cursor:
                cursor.execute("EXEC spFMPGroupViewGetRecords {0}".format(user['uid']))
                fmprecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(fmprecs, status=status.HTTP_200_OK)

class FMPStatusGrpPrevCTViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            user = payload['user']
            with connection.cursor() as cursor:
                cursor.execute("EXEC spFMPGroupViewGetPrevCTRecords {0}".format(user['uid']))
                fmprecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            
            with connection.cursor() as seasonCursor:
                seasonCursor.execute("""SELECT TOP 1 * FROM EVSeason 
                WHERE EndDate < GETDATE() 
                AND Region = (Select Region From MemberData Where UID = '{0}')
                AND Dept = 'All' ORDER BY ID DESC""".format(user['uid'],)) 
                season = [dict(zip([column[0] for column in seasonCursor.description], record)) for record in seasonCursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = {
            'season': season[0],
            'recs': fmprecs
        }
        return Response(data, status=status.HTTP_200_OK)

class FMPGetFruitsViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)    
            user = payload['user']
            
            with connection.cursor() as cursor:
                if payload['Dept'] == 'MCT':
                    if user.Internal_Position > 3:
                        # Use Django ORM for queries
                        cursor.execute("EXEC spAutoComp_CM {0}".format(user['uid']))
                        result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                    else:
                        cursor.execute("EXEC spAutoComp_CT {0}, '{1}', {2}".format(user['uid'], user['group_imwy'], user['region']))
                        result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                else:
                    if user.Internal_Position > 2:
                        cursor.execute("EXEC spAutoComp_CM {0}".format(user['uid']))
                        result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                    else:
                        cursor.execute("EXEC spAutoComp_EV {0}, {1}".format(user['uid'], user['membergroup']))
                        result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
        return Response(result, status=status.HTTP_200_OK)

class FMPGetDashStatsViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            user = payload['user']
            with connection.cursor() as cursor:
                cursor.execute("EXEC spDashGetFMPStats '{0}'".format(user['uid']))
                fmp = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(fmp[0], status=status.HTTP_200_OK)
