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
    path('getActiveServices/', g.SVCGetActiveServices.as_view()),
	path('getPeriodAttendance/', g.SVCGetPeriodAttendanceViewSet.as_view()),
	path('getGroupWeeklylog/', g.SVCGetGroupWeeklylogViewSet.as_view()),
	path('getWeekBreakdown/', g.SVCGetWeekBreakdown.as_view()),
	path('getGroupAttendance/', g.SVCGetGroupAttendance.as_view()),
 	path('updateAttendance/', g.SVCUpdateAttendanceViewSet.as_view()),
	
 
    #For Dept
    path('getWeekServices/', d.SVCGetWeekServices.as_view()),
    path('getTwoWeekServices/', d.SVCGetTwoWeekServices.as_view()),
	path('getDeptBreakdown/', d.SVCGetDeptBreakdownViewSet.as_view()),
	path('getAbsenteeByDept/', d.SVCGetAbsenteeByDept.as_view()),
	path('getAbsenteeByGroup/', d.SVCGetAbsenteeByGroup.as_view()),
	path('getLastWeekAbsenteeByGroup/', d.SVCGetLastWeekAbsenteeByGroup.as_view()),
    
	#For MT Dept
 	path('getDeptWedSunBreakdown/', mt.SVCGetDeptWedSunBreakdown.as_view()),
 	path('getLastWeekDeptWedSunBreakdown/', mt.SVCGetLastWeekDeptWedSunBreakdown.as_view()),
	path('getAbsenteeByDivision/', mt.SVCGetAbsenteeByDivision.as_view()),
	path('getWedSunAbsenteeByDivision/', mt.SVCGetWedSunAbsenteeByDivision.as_view()),
	path('getLastWeekWedSunAbsenteeByDivision/', mt.SVCGetLastWeekWedSunAbsenteeByDivision.as_view()),
 	path('getAbsentList/', mt.SVCGetAbsentList.as_view()),
  	path('getFavouritesAttendance/', mt.SVCGetFavouritesAttendance.as_view()),
  	path('getGroupAttendAbsent/', mt.SVCGroupAttendAbsent.as_view()),
    path('updateWatchList/', mt.SVCUpdateWatchList.as_view()),
]