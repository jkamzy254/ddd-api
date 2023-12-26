from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [
	path('getBB/', views.GSNewBBTDataGetBBViewSet.as_view()),
	# path('getStuds/', views.BBGetUserStudentsViewSet.as_view()),
	# path('perleaves/', views.BBStatusGrpPerLeafViewSet.as_view()),
]