from django.urls import path, include, re_path
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from django.contrib import admin
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar

router = routers.DefaultRouter()
# router.register("members", views.MemberViewSet)
router.register("seasons", views.SeasonViewSet)
router.register("bbs", views.BBDataViewSet)

# members_router = routers.NestedDefaultRouter(router, 'members', lookup="bbt")
# members_router.register("bbstudents", views.BBStudentViewSet, basename="member-bbdata")

# bbstudents_router = routers.NestedSimpleRouter(members_router, 'bbstudents', lookup='stud')
# bbstudents_router.register('bbreports', views.BBStudentViewSet, basename='bbstudents-reports')

bbs_router = routers.NestedDefaultRouter(router, 'bbs', lookup="bb")
bbs_router.register("reports", views.BBReportsViewSet, basename="bbdata-report")
# bbs_router.register("group", views.BBStatusGrpViewSet, basename="bbdata-groups")


urlpatterns = router.urls

urlpatterns = [
    path("", include(router.urls)),
    path("", include(bbs_router.urls)),
    # path("", include(members_router.urls)),
    # path("", include(bbstudents_router.urls)),
	path('bb/', include('DDD_Modules.EV.bb.urls')),
	path('fmp/', include('DDD_Modules.EV.fmp.urls')),
	path('tickets/', include('DDD_Modules.Help.tickets.urls')),
	path('members/', include('DDD_Modules.members.urls')),
	path('svc/', include('DDD_Modules.MT.svc.urls')),
	path('edu/', include('DDD_Modules.Edu.attendance.urls')),
	path('google_sheets/', include('google_sheets.urls')),
	path('tg_bot/', include('telegram_bots.urls')),
	path('apps_script/', include('apps_script.urls')),
]

# urlpatterns = [
#     path("members", views.ApiMembers.as_view()),
#     path("members/<str:pk>", views.ApiMember.as_view())
# ]