from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view

    
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
import datetime, json, pandas as pd
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv, find_dotenv
from ddd.utils import decode_jwt

load_dotenv(find_dotenv())

# Create your views here.


class BBFormAddBBReportViewSet(APIView):
    def post(self, request):
        form = request.data
        token = decode_jwt(request)

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    EXEC spBBReportAdd
                    @BBT			    = '{token['UID']}',
                    @Topic			    = '${form['bbTopic']}',
                    @ClassDate		    = '${form['bbDate']}',
                    @Label			    = '${form['bbCCT']}',
                    @NextDate		    = '${form['bbNextDate']}',
                    @CTSched            = '${form['bbCTDays']}',
                    @Reaction           = '${form['reaction']}',
                    @FKey			    = '${form['fruitId']}',
                    @AdditionalInfo    = '${form['notes']}'
                """)
                fp_rec = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(fp_rec, status=status.HTTP_200_OK)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BBFormEditBBReportViewSet(APIView):
    def post(self, request):
        form = request.data
        token = decode_jwt(request)

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    EXEC spBBReportEdit
                    @RepId			    = '{token['repId']}',
                    @BBT			    = '{token['UID']}',
                    @Topic			    = '${form['bbTopic']}',
                    @ClassDate		    = '${form['bbDate']}',
                    @Label			    = '${form['bbCCT']}',
                    @NextDate		    = '${form['bbNextDate']}',
                    @CTSched            = '${form['bbCTDays']}',
                    @Reaction           = '${form['reaction']}',
                    @FKey			    = '${form['fruitId']}',
                    @AdditionalInfo    = '${form['notes']}'
                """)
                fp_rec = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(fp_rec, status=status.HTTP_200_OK)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Django View to get an issue by its ID
class FMPGetFruitProfileViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('uid')
        
        try:
            token = decode_jwt(request)   
            with connection.cursor() as cursor:
                cursor.execute("EXEC spFMPGetFruitProfile '{0}'".format(uid))
                fp_rec = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(fp_rec, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Django View to get an issue by its ID
class FMPGetFPSeasonHistoryViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('uid')
        
        try:
            token = decode_jwt(request)   
            with connection.cursor() as cursor:
                cursor.execute("EXEC spFMPGetFPSeasonHistory '{0}'".format(uid))
                fp_rec = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(fp_rec, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FMPGetFPPreviousFruitHistoryViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('uid')
        
        try:
            token = decode_jwt(request)   
            with connection.cursor() as cursor:
                cursor.execute("EXEC spFMPGetFPPreviousFruitHistory '{0}'".format(uid))
                fp_rec = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(fp_rec, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# Django View to get an issue by its ID
class FMPGetFPBBSummaryViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('uid')
        
        try:
            token = decode_jwt(request)   
            with connection.cursor() as cursor:
                cursor.execute("EXEC spFMPGetFPBBSummary '{0}'".format(uid))
                fp_rec = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(fp_rec, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# Django View to get an issue by its ID
class FMPGetFPBBHistoryViewSet(APIView):
    def get(self, request):
        uid = request.GET.get('uid')
        
        try:
            token = decode_jwt(request)   
            with connection.cursor() as cursor:
                cursor.execute("EXEC spFMPGetFPBBHistory '{0}'".format(uid))
                fp_rec = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(fp_rec, status=status.HTTP_200_OK)
        
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FMPAssignBBTViewSet(APIView):
    def post(self, request):
        form = request.data
        token = decode_jwt(request)

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    EXEC spFMPAssignBBT
                    @UID = '{form['UID']}',
                    @BBTs = '{form['BBT_IDS']}'
                """)
                fp_rec = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(fp_rec, status=status.HTTP_200_OK)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

