from django.contrib import admin
from django.urls import path, include, re_path
from .views import hgn as h
from .views import gjn as g
from django.views.generic.base import TemplateView

from django.urls import path
import debug_toolbar


urlpatterns = [ 
    #For HGN
    path('getFinIncomeSummary/', h.FinIncomeSummary.as_view()),
    path('getFinIncomeList/', h.FinIncomeList.as_view()),
    path('getFinTransferList/', h.FinTransferList.as_view()),
    path('getFinExpenseSummary/', h.FinExpenseSummary.as_view()),
    path('getFinHgnSummaryMonth/', h.FinHgnSummaryMonth.as_view()),
    #For GJN
    path('getFinGjnInfo/', g.FinGjnInfo.as_view()),
]