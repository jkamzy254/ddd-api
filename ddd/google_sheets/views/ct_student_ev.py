from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection


# Create your views here.


class GetCurrentJDSNViewSet(APIView):
    def get(self, request):
        print(request)
        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spCurrentJDSNResults")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetRegisteredJDSNViewSet(APIView):
    def get(self, request):
        print(request)
        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spRegisteredJDSNResults")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetCTTGWViewSet(APIView):
    def get(self, request):
        print(request)
        try:
            with connection.cursor() as cursor:
                cursor.execute("EXEC spCTTGWIndResults")
                result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        