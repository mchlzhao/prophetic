from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('markets/', views.markets, name='markets'),
]
