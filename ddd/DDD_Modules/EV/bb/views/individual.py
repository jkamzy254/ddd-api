from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection


# Create your views here.
class BBGetStudentsViewSet(APIView):
    def get(self, request):
        
        try:
            token = decode_jwt(request)   
            with connection.cursor() as cursor:
                cursor.execute('EXEC spBBIndViewGetPerBBT %s', (token['UID'],))
                studs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(studs, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class BBGetBBFruitsViewSet(APIView):
    def get(self, request):
        
        try:
            token = decode_jwt(request)   
            with connection.cursor() as cursor:
                cursor.execute('EXEC spBBIndViewGetPerLeaves %s', (token['UID'],))
                studs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(studs, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class BBGetUserStudentsViewSet(APIView):
    def get(self, request):
        
        try:
            token = decode_jwt(request)   
            with connection.cursor() as cursor:
                cursor.execute("""
                               SELECT F.UID, MB.PREFERRED_NAME AS BBT, MB.UID 'BBTID', M1.PREFERRED_NAME AS L1, F.L1_ID, M2.PREFERRED_NAME AS L2, F.L2_ID, F.FishName, F.FishUser, F.FishPhone, F.EVPlatform, B.Label 
                                FROM BBData AS B 
                                LEFT JOIN MemberData AS M1 ON B.L1_ID = M1.UID 
                                LEFT JOIN MemberData AS M2 ON B.L2_ID = M2.UID 
                                LEFT JOIN MemberData AS MB ON B.BBT_ID = MB.UID 
                                LEFT JOIN FruitData F ON F.UID = B.UID 
                                WHERE B.BBT_ID = '{0}' AND B.Completed = 0
                               """.format(token['UID'],))
                studs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(studs, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)