from django.contrib import admin
from django.urls import path, include, re_path
from . import views as v
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [
    #Per group
	path('getFruitProfile/', v.FMPGetFruitProfileViewSet.as_view()),
	path('updateFruitProfile/', v.FMPUpdateFruitProfileViewSet.as_view()),
]