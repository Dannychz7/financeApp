from django.urls import path

from . import views

urlpatterns = [
    path('home', views.home, name='home'),
    path('FAQS', views.FAQ, name='FAQS'),
    path('aboutUs', views.aboutUs, name='aboutUs'),
]