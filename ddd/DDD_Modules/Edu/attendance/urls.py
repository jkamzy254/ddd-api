from django.contrib import admin
from django.urls import path, include, re_path
from .views import group as g
from .views import dept as d
from .views import edu_dept as e
from .views import shared as s
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [ 
    #Shared
	path('getWeeklyEducations/', s.EDUGetWeeklyEducationsViewSet.as_view()),    

    #For Group
    path('getActiveEducations/', g.EDUGetActiveEducations.as_view()),
	path('getGroupWeeklyLog/', g.EDUGetGroupWeeklylogViewSet.as_view()),
	path('getWeekBreakdown/', g.EDUGetWeekBreakdown.as_view()),
	path('getGroupAttendance/', g.EDUGetGroupAttendance.as_view()),
 	path('updateAttendance/', g.EDUUpdateAttendanceViewSet.as_view()),
	
 
    #For Dept
    path('getWeekEducations/', d.EDUGetWeekEducations.as_view()),
    path('getTwoWeekEducations/', d.EDUGetTwoWeekEducations.as_view()),
	path('getDeptBreakdown/', d.EDUGetDeptBreakdownViewSet.as_view()),
    
	#For Edu Dept
 	path('getDeptWeekBreakdown/', e.EDUGetDeptWeekBreakdown.as_view()),
]