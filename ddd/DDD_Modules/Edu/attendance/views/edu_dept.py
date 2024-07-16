from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection



class EDUGetDeptWeekBreakdown(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            with connection.cursor() as cursor:
                cursor.execute(f"EXEC sp_Education_GetDeptWeekBreakdown")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         
        




class EDUGetAbsentList(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            payload = request.data
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM EduAbsentList('{token['UID']}',{request.GET.get('eid')})")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)