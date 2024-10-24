from django.urls import path
from . import views


urlpatterns = [
    path('login_user', views.login_user, name="login"),
    path('register/', views.register, name='register'),
    path('buy-stock/', views.buy_stock, name='buy_stock'),
    path('sell-stock/', views.sell_stock, name='sell_stock'),
    
]