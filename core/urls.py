from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('markets/', views.markets, name='markets'),
    path('markets/create', views.MarketCreateView.as_view(), name='market_create'),
    path('markets/<int:pk>/update', views.MarketUpdateView.as_view(), name='market_update'),
    path('order_delete', views.order_delete, name='order_delete'),
]
