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
            user = Memberdata.objects.filter(id = payload['ID']).first()
            with connection.cursor() as cursor:
                cursor.execute('EXEC spFMPGroupViewGetRecords %s', (user.uid,))
                fmprecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(fmprecs, status=status.HTTP_200_OK)

class FMPStatusGrpPrevCTViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            user = Memberdata.objects.filter(id = payload['ID']).first()
            with connection.cursor() as cursor:
                cursor.execute('EXEC spFMPGroupViewGetPrevCTRecords %s', (user.uid,))
                fmprecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            
            with connection.cursor() as seasonCursor:
                seasonCursor.execute("""SELECT TOP 1 * FROM EVSeason 
                WHERE EndDate < GETDATE() 
                AND Region = (Select Region From MemberData Where UID = %s)
                AND Dept = 'All' ORDER BY ID DESC""",(user.uid,)) 
                season = [dict(zip([column[0] for column in seasonCursor.description], record)) for record in seasonCursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = {
            'season': season[0],
            'recs': fmprecs
        }
        return Response(data, status=status.HTTP_200_OK)
    
    
    # pagination_class = PageNumberPagination
