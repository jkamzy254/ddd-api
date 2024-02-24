from django.shortcuts import get_object_or_404, render
from django.http import Http404
from rest_framework.decorators import api_view
from ddd.utils import decode_jwt

from ddd.models import Memberdata

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import connection


# Create your views here.
class FMPStatusGrpViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            # user = Memberdata.objects.filter(id = payload['ID']).first()
            with connection.cursor() as cursor:
                cursor.execute("EXEC spFMPGroupViewGetRecords {0}".format(payload['UID']))
                fmprecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(fmprecs, status=status.HTTP_200_OK)

class FMPStatusGrpPrevCTViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            # user = Memberdata.objects.filter(id = payload['ID']).first()
            with connection.cursor() as cursor:
                cursor.execute("EXEC spFMPGroupViewGetPrevCTRecords {0}".format(payload['UID']))
                fmprecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
            
            with connection.cursor() as seasonCursor:
                seasonCursor.execute("""SELECT TOP 1 * FROM EVSeason 
                WHERE EndDate < GETDATE() 
                AND Region = (Select Region From MemberData Where UID = {0})
                AND Dept = 'All' ORDER BY ID DESC""".format(payload['UID'])) 
                season = [dict(zip([column[0] for column in seasonCursor.description], record)) for record in seasonCursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = {
            'season': season[0],
            'recs': fmprecs
        }
        return Response(data, status=status.HTTP_200_OK)

class FMPGetFruitsViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            user = Memberdata.objects.filter(id = payload['ID']).first()
            
            with connection.cursor() as cursor:
                if payload['Dept'] == 'MCT':
                    if 'EVLeader' in payload['roles']:
                        # Use Django ORM for queries
                        cursor.execute("EXEC spAutoComp_CT {0}, '{1}', {2}".format(payload['UID'], payload['Dept'], payload['Region']))
                        result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                    else:
                        cursor.execute("EXEC spAutoComp_CM {0}".format(payload['UID']))
                        result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                else:
                    if 'EVLeader' in payload['roles']:
                        cursor.execute("EXEC spAutoComp_EV {0}, {1}".format(payload['UID'], payload['Group']))
                        result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
                    else:
                        cursor.execute("EXEC spAutoComp_CM {0}".format(payload['UID']))
                        result = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
     
        return Response(result, status=status.HTTP_200_OK)