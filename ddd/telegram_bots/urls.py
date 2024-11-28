from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic.base import TemplateView
from django.urls import path
import debug_toolbar

from .views import jira_update as jira
from .views import google_forms_to_notion as gfn


urlpatterns = [
    #New BBT Data
	# path('jira_webhook/', jira.JiraWebHookViewSet.as_view()),
	path('jira_webhook/', jira.jira_webhook, name='jira_webhook'),
	path('av_form_webhook/', gfn.av_form_webhook, name='av_form_webhook'),
 
 
]