from django.contrib import admin
from django.urls import path, include, re_path
# from . import views
from .views import closure_after_fortnight as caf
from .views import bb_registration as br
from .views import ct_attendance as ca
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [
    #Closure After Fortnight
	path('closureGetMember/', caf.GetMemberViewSet.as_view()),
	path('closureGetStudents/', caf.GetStudentsViewSet.as_view()),
	path('closureReportStudent/', caf.ReportStudentViewSet.as_view()),
 
	#BB Registration
	path('bbRegGetMember/', br.GetMemberViewSet.as_view()),
	path('bbRegGetStudents/', br.GetStudentsViewSet.as_view()),
	path('bbRegGetSuburbs/', br.GetSuburbsViewSet.as_view()),
	path('bbRegReportStudent/', br.ReportStudentViewSet.as_view()),
 
	#CT Attendance
	path('getStudentList/', ca.CTGetStudentListViewSet.as_view()),
	path('getWeeklySchedule/', ca.CTGetWeeklyScheduleViewSet.as_view()),
	path('getAttendance/', ca.CTGetAttendanceViewSet.as_view()),
	path('updateSchedule/', ca.CTUpdateScheduleViewSet.as_view()),
	path('updateAttendance/', ca.CTUpdateAttendanceViewSet.as_view()),
	path('updateStudentStatus/', ca.CTUpdateStudentStatusViewSet.as_view()),
 
]