from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [
	path('login/', views.LoginView.as_view()),
	path('memberlist/', views.UserMembersViewSet.as_view()),
	path('groups/', views.GetGroupViewSet.as_view()),
	path('depts/', views.GetDeptViewSet.as_view()),
	path('bbgoals/', views.UserBBGoalsViewSet.as_view()),
	path('fmpgoals/', views.UserFMPGoalsViewSet.as_view()),
	path('post/', views.UserPostViewSet.as_view()),
]