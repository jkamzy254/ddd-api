from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view

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
import jwt, datetime
import json

# Create your views here.


class BBStatusGrpViewSet(APIView):
    def post(self, request):
        token = request.headers.get("authorization", None).split(" ")[1]
# token = token.split(" ")[1]
        print(token)
        
        if not token:
            raise AuthenticationFailed('Unauthorized!')

        try:
            print(token)
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthorized!')            
        user = Memberdata.objects.filter(id = payload['id']).first()
        
        try:
            with connection.cursor() as cursor:
                cursor.execute('EXEC spBBGroupViewGetRecords %s', (user.uid,))
                bbrecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(bbrecs, status=status.HTTP_200_OK)
    
    
    # pagination_class = PageNumberPagination
