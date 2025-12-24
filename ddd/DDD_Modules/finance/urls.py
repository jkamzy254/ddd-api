from django.contrib import admin
from django.urls import path, include, re_path
from .views import hgn as h
from .views import tjn as t
from .views import gjn as g
from django.views.generic.base import TemplateView
from django.urls import path
import debug_toolbar

urlpatterns = [ 
    #HGN (and above)
    path('getFinAccess/', h.FinAccess.as_view()),
    path('getFinIncomeSummary/', h.FinIncomeSummary.as_view()),
    path('getFinIncomeList/', h.FinIncomeList.as_view()),
    path('getFinTransferList/', h.FinTransferList.as_view()),
    path('getFinExpenseSummary/', h.FinExpenseSummary.as_view()),
    path('getFinClaimsList/', h.FinClaimsList.as_view()),
    path('getFinClaimPopUp/', h.FinClaimPopUp.as_view()),
    path('getFinReceiptPopUp/', h.FinReceiptPopUp.as_view()),
    path('getFinHgnSummaryMonth/', h.FinHgnSummaryMonth.as_view()),
    path('getFinBalanceSummary/', h.FinBalanceSummary.as_view()),

    path('postFinInsertIncome/', h.FinInsertIncome.as_view()),
    path('postFinInsertClaim/', h.FinInsertClaim.as_view()),
    path('postFinInsertReceipt/', h.FinInsertReceipt.as_view()),
    path('postFinInsertBalanceSS/', h.FinInsertBalanceSS.as_view()),

    path('putFinInsertSpending/', h.FinInsertSpending.as_view()),
    path('putFinDeleteBalanceSS/', h.FinDeleteBalanceSS.as_view()),
    path('putFinDeleteClaim/', h.FinDeleteClaim.as_view()),
    path('putFinDeleteDonation/', h.FinDeleteDonation.as_view()),
    path('putFinDeleteIncome/', h.FinDeleteIncome.as_view()),
    path('putFinDeleteTransfer/', h.FinDeleteTransfer.as_view()),

    path('deleteFinDeleteReceipt/', h.FinDeleteReceipt.as_view()),

    #TJN (and above)
    path('getFinReceiptCheck/', t.FinReceiptCheck.as_view()),
    path('getFinTransferCheck/', t.FinTransferCheck.as_view()),

    path('putFinConfirmReceipt/', t.FinConfirmReceipt.as_view()),

    #GJN (and above)
    path('getFinGjnInfo/', g.FinGjnInfo.as_view()),
    path('getFinChurchSummary/', g.FinChurchSummary.as_view()),
    path('getFinChurchSummaryMonth/', g.FinChurchSummaryMonth.as_view()),

    path('postFinInsertGjnNotes/', g.FinInsertGjnNotes.as_view()),

    path('putFinApproveClaim/', g.FinApproveClaim.as_view()),
    path('putFinPrintClaim/', g.FinPrintClaim.as_view()),
]