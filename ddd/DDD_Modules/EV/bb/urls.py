from django.contrib import admin
from django.urls import path, include, re_path
from .views import group as g
from .views import individual as i
from .views import shared as s
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [
    # path("", include(router.urls)),
    # path("", include(bbs_router.urls)),
    # path("", include(members_router.urls)),
    # path("", include(bbstudents_router.urls)),
	# path('bb/', include('bb.urls')),
 
    #Per Group
	path('perbbt/', g.BBStatusGrpPerBBTViewSet.as_view()),
	path('perleaves/', g.BBStatusGrpPerLeafViewSet.as_view()),
 
    #Per Individual
	path('getStuds/', i.BBGetUserStudentsViewSet.as_view()),
	path('getStudents/', i.BBGetStudentsViewSet.as_view()),
	path('getBBFruits/', i.BBGetBBFruitsViewSet.as_view()),
 
    #Shared
	path('getAllSeasons/', s.BBGetAllSeasonsViewSet.as_view()),
]