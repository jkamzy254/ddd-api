from django.contrib import admin
from django.urls import path, include, re_path
from . import views as v
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [
    #Per group
	path('addTicket/', v.AddTicketViewSet.as_view()),
	path('updateTicket/', v.UpdateTicketViewSet.as_view()),
	path('deleteTicket/', v.DeleteTicketViewSet.as_view()),
	path('addComment/', v.AddCommentViewSet.as_view()),
	path('updateComment/', v.UpdateCommentViewSet.as_view()),
	path('deleteComment/', v.DeleteCommentViewSet.as_view()),
 
	path('getMyIssues/', v.GetMyIssuesViewSet.as_view()),
	path('getGroupIssues/', v.GetGroupIssuesViewSet.as_view()),
 
]