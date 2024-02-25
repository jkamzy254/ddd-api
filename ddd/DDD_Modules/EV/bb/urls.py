from django.contrib import admin
from django.urls import path, include, re_path
from .views import group as g
from .views import individual as i
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
	path('getStuds/', g.BBGetUserStudentsViewSet.as_view()),
	path('perleaves/', g.BBStatusGrpPerLeafViewSet.as_view()),
 
    #Per Individual
	path('getStudents/', i.BBGetStudentsViewSet.as_view()),
	path('getBBFruits/', i.BBGetBBFruitsViewSet.as_view()),
	path('getAllSeasons/', i.BBGetAllSeasonsViewSet.as_view()),
]