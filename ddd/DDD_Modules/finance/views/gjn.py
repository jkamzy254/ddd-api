from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection


########### GET REQUESTS ###########

class FinGjnInfo(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            with connection.cursor() as cursor:
                cursor.execute(f"IF (SELECT Access FROM FinAccess WHERE UID = '{uid}') IN ('Church','IT') SELECT * FROM FinGjnInfo ELSE SELECT -1 ID, 'Access Denied' Message")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         
        
class FinChurchSummary(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            weekid = request.GET.get('weekid')
            with connection.cursor() as cursor:
                cursor.execute(f"IF (SELECT Access FROM FinAccess WHERE UID = '{uid}') IN ('Church','IT') EXEC spFinChurchSummary {weekid} ELSE SELECT -1 ID, 'Access Denied' Message")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class FinChurchSummaryMonth(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            yrmth = "'" + request.GET.get('yrmth') + "'" if request.GET.get('yrmth') else ''
            with connection.cursor() as cursor:
                cursor.execute(f"IF (SELECT Access FROM FinAccess WHERE UID = '{uid}') IN ('Church','IT') BEGIN EXEC spFinChurchSummaryMonth {yrmth} END ELSE SELECT -1 ID, 'Access Denied' Message")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


########### POST REQUESTS ###########


class FinInsertGjnNotes(APIView):
    def post(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            payload = request.data
            weekid = payload['weekid']
            gid = payload['gid']
            notes = payload['notes']
            with connection.cursor() as cursor:
                cursor.execute(f"IF (SELECT Access FROM FinAccess WHERE UID = '{uid}') IN ('Church','IT') BEGIN EXEC spFinInsertGjnNotes '{uid}', {weekid}, {gid}, '{notes}' END ELSE SELECT -1 ID, 'Access Denied' Message")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


########### PUT REQUESTS ###########


class FinApproveClaim(APIView):
    def put(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            payload = request.data
            claimid = payload['claimid']
            approve = payload['approve']
            with connection.cursor() as cursor:
                cursor.execute(f"IF (SELECT Access FROM FinAccess WHERE UID = '{uid}') IN ('Church','IT') BEGIN EXEC spFinApproveClaim {claimid}, {approve} END ELSE SELECT -1 ID, 'Access Denied' Message")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class FinPrintClaim(APIView):
    def put(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            payload = request.data
            claimid = payload['claimid']
            printed = payload['print']
            with connection.cursor() as cursor:
                cursor.execute(f"IF (SELECT Access FROM FinAccess WHERE UID = '{uid}') IN ('Church','IT') BEGIN EXEC spFinPrintClaim {claimid}, {printed} END ELSE SELECT -1 ID, 'Access Denied' Message")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)