from django.contrib import admin
from django.urls import path, include, re_path
# from . import views
from .views import closure_after_fortnight as caf
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [
    #Closure After Fortnight
	path('getMember/', caf.GetMemberViewSet.as_view()),
	path('getStudents/', caf.GetStudentsViewSet.as_view()),
	path('reportStudent/', caf.ReportStudentViewSet.as_view()),
 
]