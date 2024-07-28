from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection




class SVCGetDeptWedSunBreakdown(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM Service_DeptWedSunBreakdown")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class SVCGetLastWeekDeptWedSunBreakdown(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM Service_LastWeekDeptWedSunBreakdown")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
        
class SVCGetWedSunAbsenteeByDivision(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM Service_AbsenteeByDivisionWedSun")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
        
class SVCGetLastWeekWedSunAbsenteeByDivision(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM Service_LastWeekAbsenteeByDivisionWedSun")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




class SVCGetAbsenteeByDivision(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            payload = request.data
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM Service_AbsenteeByDivision({request.GET.get('sid')})")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
        
        
        
class SVCGetAbsentList(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            payload = request.data
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM AbsentList('{token['UID']}',{request.GET.get('sid')})")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
        
        
        
class SVCGetFavouritesAttendance(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM Service_FavouritesAttendance('{token['UID']}',{request.GET.get('sid')})")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
class SVCUpdateWatchList(APIView):
    def post(self, request):
        try:   
            token = decode_jwt(request)  
            payload = request.data
            with connection.cursor() as cursor:
                cursor.execute(f"sp_Service_UpdateWatchList {payload['uid']}, {payload['luuid']}, {payload['active']}")
            return Response(list(dict()), status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
        
        
        
class SVCGroupAttendAbsent(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            payload = request.data
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM Service_GroupAttendAbsent({request.GET.get('sid')})")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)