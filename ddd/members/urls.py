from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [
	path('login/', views.LoginView.as_view()),
	path('group/', views.UserMembersViewSet.as_view()),
]