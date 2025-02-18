from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection

def edu_set_absent():
    
    with connection.cursor() as cursor:
        cursor.execute("EXEC spEducation_UpdateNullToAbsent")

def edu_update_expected():
    
    with connection.cursor() as cursor:
        cursor.execute("EXEC spEducation_UpdateExpectedAttendance")

def edu_update_actual():
    
    with connection.cursor() as cursor:
        cursor.execute("EXEC spEducation_UpdateActualAttendance")

def print_awesome():
    print("You are awesome Kamau")