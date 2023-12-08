from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [
	path('group/', views.FMPStatusGrpViewSet.as_view()),
	path('getFruits/', views.FMPGetFruitsViewSet.as_view()),
	path('groupPrevCt/', views.FMPStatusGrpPrevCTViewSet.as_view()),
	path('getFMPStats/', views.FMPGetDashStatsViewSet.as_view()),
]

