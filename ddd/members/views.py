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


# Create your views here.
class LoginView(APIView):
    def post(self, request):
        warnings.filterwarnings('ignore')
        print(request.data)
        get_default_algorithms()
        username = request.data['username']
        password = request.data['password']
        print(username)
        print(password)
        user = Member.objects.filter(username=username).first()
        if user is None:
            raise AuthenticationFailed('User not found!')
        if user.password != password:
            raise AuthenticationFailed('Incorrect password')

        uid = pd.read_sql(f"SELECT UID FROM LoginData WHERE Username = '{username}'",connection).iloc[0,0]
        otp_response = send_otp(uid)
        if otp_response.status_code == status.HTTP_200_OK:
            return Response({'uid':uid}, status=status.HTTP_200_OK)
        else:
            return Response("Failed to send OTP.", status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTP(APIView):
    def post(self, request):
        warnings.filterwarnings('ignore')
        print(request.data)
        get_default_algorithms()
        uid = request.data['uid']
        otp = request.data['otp']
        print(f'uid = {uid}')
        print(f'otp = {otp}')
        wlid = []

        try:
            otp_dataframe = pd.read_sql(f"""SELECT TOP 1 OTP FROM OtpLog WHERE UID = '{uid}'
        AND ValidUntil > CONVERT(DateTime, SYSDATETIMEOFFSET() AT TIME ZONE 'AUS Eastern Standard Time') ORDER BY ValidUntil DESC""",connection)
            if len(otp_dataframe) == 0:
                print("OTP Expired")
                return Response('OTP Expired!', status=status.HTTP_400_BAD_REQUEST)

            otp_db = int(otp_dataframe.iloc[0,0])
            print(f'otp_db = {otp_db}, type = {type(otp_db)}')
            print(f'otp = {otp}, type = {type(otp)}')

            if int(otp) != otp_db:
                print("Invalid OTP")
                return Response('Invalid OTP!', status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"An Error occurred: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            wl = WL.objects.filter(wid__in=WLR.objects.filter(memberid=uid))
            with connection.cursor() as cursor:
                cursor.execute("""SELECT MemberID, WLID FROM WhiteListRecData WHERE WLID IN (SELECT WID FROM WhiteListData WHERE Title IN ('All','CSAM'))
                                    UNION
                                    SELECT UID MemberID, PID WLID FROM TGWPositionLog WHERE EndDate IS NULL AND PID IN (6,8,9,20,22,24)
                                """)
                pid = pd.DataFrame(cursor.fetchall())
                pid.columns = [i[0] for i in cursor.description]
                pid = pid[pid['MemberID']==uid]
                print( pid['WLID'].values[0])
            for i in wl:
                wlid.append(i.title)
            member = Member.objects.filter(uid = uid).first()
            evid = member.id
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

            # refresh = token.for_user(user)

            # Generate an access token
            # token = str(refresh.access_token)

            payload = {
                "ID":evid,
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