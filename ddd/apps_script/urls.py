from django.contrib import admin
from django.urls import path, include, re_path
# from . import views
from .views import closure_after_fortnight as caf
from .views import bb_registration as br
from .views import ct_attendance as ca
from .views import edu_player as ep
from .views import edu_dept_bbt as eb
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
	path('ctGetMember/', ca.GetMemberViewSet.as_view()),
	path('ctGetStudentList/', ca.CTGetStudentListViewSet.as_view()),
	path('ctGetWeeklySchedule/', ca.CTGetWeeklyScheduleViewSet.as_view()),
	path('ctGetAttendance/', ca.CTGetAttendanceViewSet.as_view()),
	path('ctGetAttendanceSummary/', ca.CTGetAttendanceSummaryViewSet.as_view()),
	path('ctGetStudHistory/', ca.CTGetStudHistoryViewSet.as_view()),
	path('ctGetStudent/', ca.CTGetStudentViewSet.as_view()),
	path('ctUpdateSchedule/', ca.CTUpdateScheduleViewSet.as_view()),
	path('ctUpdateAttendance/', ca.CTUpdateAttendanceViewSet.as_view()),
	path('ctUpdateStudentStatus/', ca.CTUpdateStudentStatusViewSet.as_view()),
	path('ctSummaryGetAllDays/', ca.CTSummaryGetAllDaysViewSet.as_view()),
	path('ctSummaryGetClass/', ca.CTSummaryGetClassViewSet.as_view()),
	path('ctSummaryGetClassSummary/', ca.CTSummaryGetClassSummaryViewSet.as_view()),
	path('ctGetCCTTransition/', ca.CTGetCCTTransitionViewSet.as_view()),
 
	#Edu Player
	path('eduGetMember/', ep.GetMemberViewSet.as_view()),
	path('eduVideoGetFolders/', ep.EduVideoGetFoldersViewSet.as_view()),  
	path('eduVideoGetLogs/', ep.EduVideoGetLogsViewSet.as_view()),  
	path('eduVideoGetFaves/', ep.EduVideoGetFavesViewSet.as_view()),   
	path('eduVideoUpdateLogs/', ep.EduVideoUpdateLogViewSet.as_view()),   
	path('eduVideoUpdateFaves/', ep.EduVideoUpdateFavesViewSet.as_view()),   
 
	#Edu Dept BBT System
	path('eduBBTGetMember/', eb.GetMemberViewSet.as_view()),
	path('eduBBTGetBBTData/', eb.GetBBTDataViewSet.as_view()),
	path('eduBBTGetCurrentCTData/', eb.GetCurrentCTDataViewSet.as_view()),  
	path('eduBBTGetAllActiveCTData/', eb.GetAllActiveCTDataViewSet.as_view()),  
	path('eduBBTGetBB/', eb.GetBBViewSet.as_view()),  
	path('eduBBTGetCurrentCTs/', eb.GetCurrentCTsViewSet.as_view()),  
	path('eduBBTGetBBTMasterList/', eb.GetBBTMasterListViewSet.as_view()),  
	path('eduBBTCheckTransferBBT/', eb.CheckBBTTransferViewSet.as_view()),  
	path('eduBBTTransferBBT/', eb.BBTransferBBTViewSet.as_view()),  
	path('eduBBTUpdateStatus/', eb.UpdateBBTStatusViewSet.as_view()),  
	path('eduBBTCheckTransferCT/', eb.CheckCTTransferViewSet.as_view()),  
	path('eduBBTTransferCenter/', eb.BBTransferCenterViewSet.as_view()), 
	path('eduBBTGetCurrentCCT/', eb.GetCurrentCCTUIDViewSet.as_view()),   
	path('eduBBTUpdateCCTEdu/', eb.UpdateCCTEduViewSet.as_view()),    
	# path('eduVideoUpdateFaves/', ep.EduVideoUpdateFavesViewSet.as_view()),   
 
]