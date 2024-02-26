from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection


# Create your views here.
class SVCGetDeptBreakdownViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM Service_DeptBreakdown(%s)', (payload['UID'],))
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]

            return Response(recs, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
