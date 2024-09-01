from django.contrib import admin
from django.urls import path, include, re_path
# from . import views
from .views import jira_update as jira
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [
    #New BBT Data
	# path('jira_webhook/', jira.JiraWebHookViewSet.as_view()),
	path('jira_webhook/', jira.jira_webhook, name='jira_webhook'),
	# path('getBTMFMP/', nbd.GetBTMFMPViewSet.as_view()),
	# path('getBBTData/', nbd.GetBBTDataViewSet.as_view()),
	# path('getBBNotFallen/', nbd.GetBBNotFallenViewSet.as_view()),
 
 
]