from django.contrib import admin
from django.urls import path, include, re_path
# from . import views
from .views import closure_after_fortnight as caf
from .views import bb_registration as br
from .views import ct_attendance as ca
from .views import edu_player as ep
from .views import edu_dept_bbt as eb
from .views import tribe_exam as ex
from .views import mlt as mlt
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
	path('ctGetTransitionCTDets/', ca.CTGetTransitionCTDetsViewSet.as_view()),
	path('ctUpdateTransitionCT/', ca.UpdateTransitionCTViewSet.as_view()),
 
	#HSP
	path('eduGetMember/', ep.GetMemberViewSet.as_view()),
	path('hspGetFolders/', ep.HSPGetFoldersViewSet.as_view()),  
	path('hspGetLogs/', ep.HSPGetLogsViewSet.as_view()),  
	path('hspGetFaves/', ep.HSPGetFavesViewSet.as_view()),   
	path('hspUpdateLogs/', ep.HSPUpdateLogViewSet.as_view()),   
	path('hspUpdateFaves/', ep.HSPUpdateFavesViewSet.as_view()),  
	path('hspGetEdu/', ep.HSPGetActiveEdus.as_view()),   
	path('hspGetGroupAttendance/', ep.HSPGetGroupAttendance.as_view()),  
	path('hspGetMembers/', ep.HSPGetMembers.as_view()), 
	path('hspUpdateAttendance/', ep.HSPUpdateAttendanceViewSet.as_view()),  
	path('hspExamGetGroup/', ep.HSPExamGroupViewSet.as_view()),   
	path('hspExamGetMyGroup/', ep.HSPExamMyGroupViewSet.as_view()),  
	path('hspExamUpdateScore/', ep.HSPExamUpdateScoreViewSet.as_view()),
	path('hspSummary/', ep.HSPSummaryViewSet.as_view()),   
	path('hspGetMaterial/', ep.HSPGetMaterialViewSet.as_view()),
	path('hspFetchFile/', ep.HSPFetchFileViewSet.as_view()), 
	path('hspUploadFile/', ep.HSPUploadFileViewSet.as_view()),     
	path('hspGetSubmissionsInd/', ep.HSPGetSubmissionsIndViewSet.as_view()), 
	path('hspGetSubmissionsAll/', ep.HSPGetSubmissionsAllViewSet.as_view()),  
	path('hspUpdateComment/', ep.HSPUpdateCommentViewSet.as_view()),   
	path('hspGetExpIndSum/', ep.HSPDropInExpIndSumViewSet.as_view()),   
	path('hspGetExpDept/', ep.HSPDropInExpDeptViewSet.as_view()),     
	path('hspGetDeptSubmission/', ep.HSPDeptVidSubmissionViewSet.as_view()),    
	path('hspGetWeeklySessions/', ep.HSPGetEduWeeklySessionsViewSet.as_view()),   
	path('hspGetSessionScores/', ep.HSPGetEduSessionScoresViewSet.as_view()),   
	path('hspGetMWScores/', ep.HSPGetMWScoresViewSet.as_view()),    
     
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
 
	#Tribe Exam System
	path('examGetMember/', ex.GetMemberViewSet.as_view()),
	path('examGetGroupView/', ex.GetGroupViewSet.as_view()),
	path('examGetMyGroup/', ex.GetMyGroupViewSet.as_view()),
	path('examUpdateScore/', ex.UpdateExamScoreViewSet.as_view()),
	path('examUpdateScoreSheets/', ex.UpdateExamScoreSheetsViewSet.as_view()),
 
	#MLT
	path('mltGetMember/', mlt.MLTGetMemberViewSet.as_view()), 
	path('mltGetMaterial/', ep.MLTGetMaterialViewSet.as_view()),
 
]