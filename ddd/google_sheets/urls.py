from django.contrib import admin
from django.urls import path, include, re_path
# from . import views
from .views import new_bbt_data as nbd
from .views import ct_student_ev as cse
from .views import cct_edu as ce
from .views import fruit_basket as fb
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [
    #New BBT Data
	path('getBB/', nbd.GetBBViewSet.as_view()),
	path('getBTMFMP/', nbd.GetBTMFMPViewSet.as_view()),
	path('getBBTData/', nbd.GetBBTDataViewSet.as_view()),
	path('getBBNotFallen/', nbd.GetBBNotFallenViewSet.as_view()),
	path('getCurrentCCT/', nbd.GetCurrentCCTViewSet.as_view()),
	path('getBTMList/', nbd.GetBTMListViewSet.as_view()),
 	path('getCurrentCTData/', nbd.GetCurrentCTDataViewSet.as_view()),
  	path('getFebCTData/', nbd.GetFebCTDataViewSet.as_view()),
  	path('getPotentialBTM/', nbd.GetPotentialBTMViewSet.as_view()),
  	path('getCCTInactive/', nbd.GetCCTInactiveViewSet.as_view()),
  	path('getCurrentCTBBTData/', nbd.GetCurrentCTBBTDataViewSet.as_view()),
  	path('getP/', nbd.GetPViewSet.as_view()),
  	path('getBTMFruits/', nbd.GetBTMFruitsViewSet.as_view()),
  	path('getBBTMasterList/', nbd.GetBBTMasterListViewSet.as_view()),
  	path('updateBBTMasterList/', nbd.UpdateBBTMasterListViewSet.as_view()),
  	path('getDenomEthnic/', nbd.GetDenomEthnicViewSet.as_view()),
 

	#CT Student EV
	path('getCurrentJDSN/', cse.GetCurrentJDSNViewSet.as_view()),
	path('getRegisteredJDSN/', cse.GetRegisteredJDSNViewSet.as_view()),
	path('getCTTGW/', cse.GetCTTGWViewSet.as_view()),
 
	#Current CT - Edu
	path('getCurrentCCTEdu/', ce.GetCurrentCCTEduViewSet.as_view()),
 
	#Fruit Basket
	path('getBBStats/', fb.GetBBStatsViewSet.as_view()),
 
 
 
]