from django.contrib import admin
from django.urls import path, include, re_path
from .views import group as g
from .views import individual as i
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [
    #Per group
	path('group/', g.FMPStatusGrpViewSet.as_view()),
	path('getFruits/', g.FMPGetFruitsViewSet.as_view()),
	path('groupPrevCt/', g.FMPStatusGrpPrevCTViewSet.as_view()),
 
    #Per individual
	path('getIndFruits/', i.FMPGetFruitsViewSet.as_view()),
	path('getPrevCtFruits/', i.FMPGetPrevCTFruitsViewSet.as_view()),
]