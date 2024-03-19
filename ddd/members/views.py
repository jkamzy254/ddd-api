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
import warnings
from .mfa.mfa import send_otp
from api.redis import Redis


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

        user = Member.objects.filter(username=username).first()
        wl = WL.objects.filter(wid__in=WLR.objects.filter(memberid=user.id))
        print(wl)
        for i in wl:
            wlid.append(i.title)
        member = Member.objects.filter(id = user.id).first()
        print(member.internal_position)
        if member.internal_position == 1 or (member.membergroup == 'Department' and member.tgw and member.condition == 'Active') or 'All' in wlid:
            wlid.append('Leader')
        if int(member.internal_position) < 3 or 'All' in wlid:
            wlid.append('EVLeader')
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
            "UID":user.uid,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=(60*24)),
            'iat': datetime.datetime.utcnow(),
            'user': serializer.data,
            'roles': wlid
        }

        token = ('Bearer '+encode_jwt(payload).decode()).encode()
        response = Response()
        otp_response = send_otp(user.uid)
        response.set_cookie(key='token',value=token, httponly=True)
        response.data = {'token': token}
        return response

class OTP(APIView):
    def post(self, request):
        uid = request.data['uid']
        print(uid)

        return send_otp(uid)

class VerifyOTP(APIView):
    def post(self, request):
        warnings.filterwarnings('ignore')

        try:
            payload = decode_jwt(request)
            userID = payload['UID']
            otp = request.data['otp']

            otp_dataframe = pd.read_sql(f"""SELECT TOP 1 OTP FROM OtpLog WHERE UID = '{userID}'
        AND ValidUntil > CONVERT(DateTime, SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time') ORDER BY ValidUntil DESC""",conn)
            if len(otp_dataframe) == 0:
                print("OTP Expired")
                return Response('OTP Expired!', status=status.HTTP_400_BAD_REQUEST)

            otp_db = otp_dataframe.iloc[0,0]

            if otp != otp_db:
                print("Invalid OTP")
                return Response('Invalid OTP!', status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            print("Authentication successful")
            authenticated_hash = hash(userID + str(request.data['otp']))
            Redis.hset('getAuthenticatedUser', userID, authenticated_hash)
            return Response(authenticated_hash, status=status.HTTP_200_OK)


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