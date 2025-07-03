from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection

def ct_add_classes():
    print("Printing Connection as Cursor for spCTScheduleAddClasses")
    with connection.cursor() as cursor:
        cursor.execute("EXEC spCTScheduleAddClasses")
    print("Just ran Connection as Cursor for spCTScheduleAddClasses")
        
