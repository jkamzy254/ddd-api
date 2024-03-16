from django.contrib import admin
from django.urls import path, include, re_path
from .views import group as g
from .views import dept as d
from .views import mt_dept as mt
from .views import shared as s
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [ 
    #Shared
	path('getWeeklyServices/', s.SVCGetWeeklyServicesViewSet.as_view()),    

    #For Group
	path('getPeriodAttendance/', g.SVCGetPeriodAttendanceViewSet.as_view()),
	path('getGroupWeeklylog/', g.SVCGetGroupWeeklylogViewSet.as_view()),
	path('updateAttendance/', g.SVCUpdateAttendanceViewSet.as_view()),
 
    #For Dept
	path('getDeptBreakdown/', d.SVCGetDeptBreakdownViewSet.as_view()),
    
	#For MT Dept
]