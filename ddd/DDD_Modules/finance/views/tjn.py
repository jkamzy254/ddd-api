from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection


########### GET REQUESTS ###########



class FinReceiptCheck(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            subdivision = request.GET.get('subdivision') if 'subdivision' in request.GET else '%'
            with connection.cursor() as cursor:
                cursor.execute(f"IF (SELECT Access FROM FinAccess WHERE UID = '{uid}') IN ('Church','IT')  SELECT * FROM FinReceiptCheck('{subdivision}') ELSE SELECT -1 ID, 'Access Denied' Message")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class FinTransferCheck(APIView):
    def get(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            subdivision = request.GET.get('subdivision') if 'subdivision' in request.GET else '%'
            with connection.cursor() as cursor:
                cursor.execute(f"IF (SELECT Access FROM FinAccess WHERE UID = '{uid}') IN ('Church','IT') SELECT * FROM FinTransferCheck('{subdivision}') ELSE SELECT -1 ID, 'Access Denied' Message")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


########### PUT REQUESTS ###########



class FinConfirmReceipt(APIView):
    def put(self, request):
        try:
            token = decode_jwt(request)
            uid = token['UID']
            payload = request.data
            receiptid = payload['receiptid']
            physical = payload['physical']
            notes = payload['notes']
            with connection.cursor() as cursor:
                cursor.execute(f"IF (SELECT Access FROM FinAccess WHERE UID = '{uid}') IN ('Church','IT') EXEC spFinConfirmReceipt {receiptid}, {physical}, '{notes}' ELSE SELECT -1 ID, 'Access Denied' Message")
                res = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            return Response(res, status=status.HTTP_200_OK)
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            print(e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)