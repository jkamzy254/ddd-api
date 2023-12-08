from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [
    # path("", include(router.urls)),
    # path("", include(bbs_router.urls)),
    # path("", include(members_router.urls)),
    # path("", include(bbstudents_router.urls)),
	# path('bb/', include('bb.urls')),
	path('perbbt/', views.BBStatusGrpPerBBTViewSet.as_view()),
	path('getStuds/', views.BBGetUserStudentsViewSet.as_view()),
	path('perleaves/', views.BBStatusGrpPerLeafViewSet.as_view()),
	path('youthBB/', views.BBGetYouthBBViewSet.as_view()),
	path('getME/', views.BBGetMEViewSet.as_view()),
]