from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view
from ddd.utils import encode_jwt
from rest_framework_simplejwt.tokens import RefreshToken
from jwt.algorithms import get_default_algorithms

from ddd.utils import encode_jwt, decode_jwt

from .serializers import MemberSerializer
    
from ddd.models import Memberdata, Evseason, Bbdata, Report
from ddd.models import Memberuserdata as User
from ddd.models import Memberdata as Member
from ddd.models import Whitelistdata as WL
from ddd.models import Whitelistrecdata as WLR
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.db import connection
import jwt, datetime, json, pandas as pd


# Create your views here.
class LoginView(APIView):
    def post(self, request):
        print(request.data)
        get_default_algorithms()
        username = request.data['username']
        password = request.data['password']
        print(username)
        print(password)
        wlid = []
        conn = connection.cursor();
        
        user = Member.objects.filter(username=username).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        print(user)
        wl = WL.objects.filter(wid__in=WLR.objects.filter(memberid=user.uid))
        with connection.cursor() as cursor:
            cursor.execute("""SELECT MemberID, WLID FROM WhiteListRecData WHERE WLID IN (SELECT WID FROM WhiteListData WHERE Title IN ('All','CSAM'))
                                UNION
                                SELECT UID MemberID, PID WLID FROM TGWPositionLog WHERE EndDate IS NULL AND PID IN (6,8,9,20,22,24)
                            """)
            pid = pd.DataFrame(cursor.fetchall())
            pid.columns = [i[0] for i in cursor.description]
            pid = pid[pid['MemberID']==user.uid]
            print( pid['WLID'].values[0])
        for i in wl:
            wlid.append(i.title)
        member = Member.objects.filter(id = user.id).first()
        print(member.internal_position)
        if member.internal_position == 1 or (member.membergroup == 'Department' and member.tgw and member.condition == 'Active') or 'All' in wlid:
            wlid.append('Leader')
        if int(member.internal_position) < 2 or 'All' in wlid:
            wlid.append('EVLeader')
        if pid['WLID'].values[0] >= 6:
            wlid.append('IDept')
        if pid['WLID'].values[0] >= 8:
            wlid.append('Dept')
        if pid['WLID'].values[0] >= 20:
            wlid.append('Church')
        if member.bbt or 'All' in wlid:
            wlid.append('BBT')
        serializer = MemberSerializer(member)     
        
        if user is None:
            raise AuthenticationFailed('User not found!')

        if user.password != password:
            raise AuthenticationFailed('Incorrect password')
        
        # refresh = token.for_user(user)

        # Generate an access token
        # token = str(refresh.access_token)

        payload = {
            "ID":user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=(60*24)),
            'iat': datetime.datetime.utcnow(),
            'user': serializer.data,
            'roles': wlid
        }
        token = ('Bearer '+encode_jwt(payload).decode()).encode()
        response = Response()
        response.set_cookie(key='token',value=token, httponly=True)
        response.data = {'token': token}
        return response


class UserMembersViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            # user = Memberdata.objects.filter(id = payload['ID']).first()
            with connection.cursor() as cursor:
                cursor.execute("EXEC spUserGroupViewGetMembers {0}".format(payload['UID']))
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(recs, status=status.HTTP_200_OK)


class GetGroupViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            # user = Memberdata.objects.filter(id = payload['ID']).first()
            with connection.cursor() as cursor:
                cursor.execute("EXEC spUserGroupViewGetGroups {0}".format(payload['UID']))
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(recs, status=status.HTTP_200_OK)


class GetDeptViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            # user = Memberdata.objects.filter(id = payload['ID']).first()
            with connection.cursor() as cursor:
                cursor.execute("EXEC spUserGroupViewGetDepts {0}".format(payload['UID']))
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(recs, status=status.HTTP_200_OK)


class GetSDivisionViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            # user = Memberdata.objects.filter(id = payload['ID']).first()
            with connection.cursor() as cursor:
                cursor.execute("EXEC spUserGroupViewGetSDivisions {0}".format(payload['UID']))
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(recs, status=status.HTTP_200_OK)

class UserBBGoalsViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            # user = Memberdata.objects.filter(id = payload['ID']).first()
            with connection.cursor() as cursor:
                cursor.execute("EXEC spUserGroupViewGetGoals {0}".format(payload['UID']))
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(recs, status=status.HTTP_200_OK)

class UserFMPGoalsViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            # user = Memberdata.objects.filter(id = payload['ID']).first()
            with connection.cursor() as cursor:
                cursor.execute("EXEC spUserGroupViewGetFMPGoals {0}".format(payload['UID']))
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(recs, status=status.HTTP_200_OK)

class UserPostViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            # user = Memberdata.objects.filter(id = payload['ID']).first()
            with connection.cursor() as cursor:
                cursor.execute("EXEC spUserGroupViewGetPost {0}".format(payload['UID']))
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(recs, status=status.HTTP_200_OK)


class UserGetFishersViewSet(APIView):
    def get(self, request):
        
        try:
            payload = decode_jwt(request)   
            # user = Memberdata.objects.filter(id = payload['ID']).first()
            with connection.cursor() as cursor:
                cursor.execute("EXEC spAutoCompM {0}".format(payload['Region']))
                recs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(recs, status=status.HTTP_200_OK)