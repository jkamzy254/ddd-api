from django.contrib import admin
from django.urls import path, include, re_path
from . import views as v
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [
    #Per group
	path('getFruitProfile/', v.FMPGetFruitProfileViewSet.as_view()),
	path('updateFruitProfile/', v.FMPUpdateFruitProfileViewSet.as_view()),
 
	path('getSeasonHistory/', v.FMPGetFPSeasonHistoryViewSet.as_view()),
	path('getPreviousFruitHistory/', v.FMPGetFPPreviousFruitHistoryViewSet.as_view()),
	path('assignBBT/', v.FMPAssignBBTViewSet.as_view()),
 
	path('getBBSummary/', v.FMPGetFPBBSummaryViewSet.as_view()),
	path('getBBHistory/', v.FMPGetFPBBHistoryViewSet.as_view()),
 
	path('updateCT/', v.FMPSeasonUpdateLogViewSet.as_view()),
	path('updateSchedule/', v.FMPCTScheduleUpdateLogViewSet.as_view()),

]