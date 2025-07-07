from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection

def svc_set_absent():
    
    with connection.cursor() as cursor:
        cursor.execute("EXEC DailyNullToAbsent")

def svc_update():
    
    with connection.cursor() as cursor:
        cursor.execute("EXEC spService_UpdateServices")

def cron_test():
    print("Cron Test: MT Side")