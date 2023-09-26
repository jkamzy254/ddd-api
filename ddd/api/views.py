from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view

from api.filters import MemberFilter, BBDataFilter, SeasonFilter, ReportFilter
from .serializers import MemberSerializer, EvseasonSerializer, BBDataSerializer, ReportSerializer,BBGroupSerializer
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
import jwt, datetime
import json

class MemberViewSet(ModelViewSet):
    queryset = Memberdata.objects.all()
    serializer_class = MemberSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MemberFilter
    search_fields = ["region","group_imwy"]
    ordering_fields = ["internal_position","group_imwy"]
    # pagination_class = PageNumberPagination

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_value = self.kwargs[self.lookup_field]
        queryset = queryset.filter(uid=lookup_value)
        try:
            obj = queryset.get()
        except Memberdata.DoesNotExist:
            raise Http404("Object not found.")
        
        self.check_object_permissions(self.request, obj)
        return obj

class BBDataViewSet(ModelViewSet):
    queryset = Bbdata.objects.all()
    serializer_class = BBDataSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BBDataFilter
    search_fields = ["region","fruitname"]
    ordering_fields = ["season"]
    pagination_class = PageNumberPagination

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        lookup_value = self.kwargs[self.lookup_field]
        queryset = queryset.filter(uid=lookup_value)
        try:
            obj = queryset.get()
        except Bbdata.DoesNotExist:
            raise Http404("Object not found.")
        
        self.check_object_permissions(self.request, obj)
        return obj
    
# class BBStudentViewSet(ModelViewSet):
    # print()
    # queryset = Bbdata.objects.all()
    # serializer_class = BBDataSerializer
    
    # def get_serializer_context(self):
    #     print(self.kwargs["bbt_pk"])
    #     return {"bbt_id": self.kwargs["bbt_pk"]}
    
class BBStudentsViewSet(ModelViewSet):
    serializer_class = BBDataSerializer
    
    def get_queryset(self):
        print(self.kwargs["bbt_pk"])
        return Bbdata.objects.filter(bbt_id=self.kwargs["bbt_pk"]).select_related('bbt_id')
    
    def get_serializer_context(self):
        return {"bbt_id": self.kwargs["bbt_pk"]}
    
class BBStudentViewSet(ModelViewSet):
    serializer_class = BBDataSerializer
    
    def get_queryset(self):
        print(self.kwargs)
        return Bbdata.objects.filter(bbt_id=self.kwargs["bbt_pk"]).select_related('bbt_id')
    
    def get_serializer_context(self):
        print(self.kwargs["bbt_pk"])
        return {"bbt_id": self.kwargs["bbt_pk"]}

class SeasonViewSet(ModelViewSet):
    queryset = Evseason.objects.all()
    serializer_class = EvseasonSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SeasonFilter
    search_fields = ["region","dept"]
    ordering_fields = ["id","startdate"]
    pagination_class = PageNumberPagination

class ReportViewSet(ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ReportFilter
    search_fields = ["topic"]
    ordering_fields = ["reportid","classdate"]

# class BBReportsViewSet(ModelViewSet):
#     queryset = Report.objects.all()
#     serializer_class = ReportSerializer
    
#     def get_serializer_context(self):
#         print(self.kwargs)
#         return {"uid": self.kwargs["bb_pk"]}

class BBReportsViewSet(ModelViewSet):
    serializer_class = ReportSerializer
    
    def get_queryset(self):
        print(self.kwargs["bbt_pk"])
        return Report.objects.filter(uid=self.kwargs["bbt_pk"])
    
    def get_serializer_context(self):
        print(self.kwargs)
        return {"uid": self.kwargs["bb_pk"]}
    
class BBStatusGrpViewSet(ViewSet):
    def list(self, request):
        token = request.COOKIES.get('token')
        
        if not token:
            raise AuthenticationFailed('Unauthorized!')

        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthorized!')
        
        try:
            with connection.cursor() as cursor:
                cursor.execute('EXEC spGevaGetMember %s', (payload['id'],))
                bbrecs = [dict(zip([column[0] for column in cursor.description], record)) for record in cursor.fetchall()]
        except Exception as e:
            # Handle exceptions here, e.g., logging or returning an error response
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(bbrecs, status=status.HTTP_200_OK)
    
    
    # pagination_class = PageNumberPagination

# class ApiMembers(ListCreateAPIView):
#     queryset = Memberdata.objects.all()
#     serializer_class = MemberSerializer

# class ApiMember(RetrieveUpdateDestroyAPIView):
#     queryset = Memberdata.objects.all()
#     serializer_class = MemberSerializer
    

# class ApiMembers(APIView):
#     def get(self, request):
#         members = Memberdata.objects.all()
#         serializer = MemberSerializer(members, many=True)
#         return Response(serializer.data)
    
#     def post(self, request):
#         serializer = MemberSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

# class ApiMember(APIView):
#     def get(self, request,mk):
#         member = get_object_or_404(Memberdata,id=mk)
#         serializer = MemberSerializer(member)
#         return Response(serializer.data)
    
#     def put(self, request,mk):
#         member = get_object_or_404(Memberdata,id=mk)
#         serializer = MemberSerializer(member, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
    
#     def delete(self, request,mk):
#         member = get_object_or_404(Memberdata,id=mk)
#         member.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# Create your views here.
class LoginView(APIView):
    def post(self, request):
        print(request.data)
        username = request.data['username']
        password = request.data['password']
        print(username)
        print(password)
        wlid = []
        
        user = User.objects.filter(username=username).first()
        print(user)
        wl = WL.objects.filter(wid__in=WLR.objects.filter(memberid=user.uid))
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

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=(60*24)),
            'iat': datetime.datetime.utcnow(),
            'user': serializer.data,
            'roles': wlid
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')
        response = Response()
        response.set_cookie(key='token',value=token, httponly=True)
        response.data = {'token': token}
        return response
   