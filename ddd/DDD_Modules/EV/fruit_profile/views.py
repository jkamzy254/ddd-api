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
import base64
import requests
from jira import JIRA, JIRAError
from jira.resources import Issue
from ddd.utils import decode_jwt

load_dotenv(find_dotenv())

# Create your views here.

def get_jira_client():
    jira_options = {'server': os.environ.get('JIRA_URL')}
    jira = JIRA(options=jira_options, basic_auth=(os.environ.get('JIRA_USERNAME'), os.environ.get('TICKET_TOKEN')))
    return jira

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

class FMPUpdateFruitProfileViewSet(APIView):
    def post(self, request):
        form = request.data
        token = decode_jwt(request)

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    EXEC spFMPUpdateMPForm
                    @UID = '{form['uid']}',
                    @Nationality = '{form['nationality']}',
                    @DOB = '{form['dob']}',
                    @Location = '{form['location']}',
                    @Work = '{form['work']}',
                    @Uni = '{form['uni']}',
                    @Church = '{form['church']}',
                    @Personality = '{form['personality']}',
                    @Schedule = '{form['schedule']}',
                    @Mental = '{form['mental']}',
                    @Crypto = '{form['crypto']}',
                    @Spirituality = '{form['spirituality']}',
                    @BBTIntro = '{form['bbtintro']}',
                    @PrefBBT = '{form['prefbbt']}',
                    @PickingDateTime = '{form['pickingdatetime']}',
                    @PickingLocation = '{form['pickinglocation']}',
                    @ReporterID = '{token['UID']}'
                """)
                fp_rec = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(fp_rec, status=status.HTTP_200_OK)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FMPUpdateFruitDataViewSet(APIView):
    def post(self, request):
        form = request.data
        token = decode_jwt(request)

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"""
                    EXEC spFMPUpdateFruitRecord
                    @UID = '{form['uid']}',
                    @FishName = '{form['name']}',
                    @Nationality = '{form['nationality']}',
                    @DOB = '{form['dob']}',
                    @F_TIME = '{form['f_time']}',
                    @Gender = '{form['gender']}',
                    @Visa = '{form['visa']}',
                    @Denomination = '{form['denomination']}',
                    @Notes = '{form['notes']}',
                    @Location = '{form['location']}',
                    @PicID = '{form['picid']}',
                    @ReporterID = '{token['UID']}'
                """)
                fp_rec = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(fp_rec, status=status.HTTP_200_OK)

        except Exception as e:
            print(str(e))
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

class FMPSeasonUpdateLogViewSet(APIView):
    def post(self, request):
        form = request.data
        token = decode_jwt(request)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spFMPSeasonUpdateLog @UID = %s, @SsnID = %s, @BBTs = %s""", [form.get('UID'), form.get('Season'), token['UID']])
                update = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(update, status=status.HTTP_200_OK)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FMPCTScheduleUpdateLogViewSet(APIView):
    def post(self, request):
        form = request.data
        token = decode_jwt(request)

        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spFMPSeasonUpdateLog @UID = %s, @CTDays = %s, @BBTs = %s""", [form.get('UID'), form.get('CTDays'), token['UID']])
                update = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(update, status=status.HTTP_200_OK)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


