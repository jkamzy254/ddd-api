from django.contrib import admin
from django.urls import path, include, re_path
# from . import views
from .views import new_bbt_data as nbd
from .views import ct_student_ev as cse
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [
	path('getBB/', nbd.GetBBViewSet.as_view()),
 
	path('getCurrentJDSN/', cse.GetCurrentJDSNViewSet.as_view()),
	path('getRegisteredJDSN/', cse.GetRegisteredJDSNViewSet.as_view()),
	path('getCTTGW/', cse.GetCTTGWViewSet.as_view()),
	# path('perleaves/', views.BBStatusGrpPerLeafViewSet.as_view()),
 
 
]