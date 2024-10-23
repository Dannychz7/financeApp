from django.urls import path
from . import views

urlpatterns = [
    path('transactionHistory', views.transactionHistory, name='transactionHistory'),
    path("transactions/", views.TransactionHistory, name="TransactionHistory"),
]