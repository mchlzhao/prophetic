from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.GroupCreateView.as_view(), name='group_create'),
    path('groups/<int:group_id>/', views.event_list, name='event_list'),
    path('groups/<int:group_id>/events/create/', views.event_create, name='event_create'),
    path('markets/', views.markets, name='markets'),
    path('markets/create/', views.MarketCreateView.as_view(), name='market_create'),
    path('markets/<int:pk>/update/', views.MarketUpdateView.as_view(), name='market_update'),
    path('order_delete/', views.order_delete, name='order_delete'),
    path('markets/orders/', views.get_market_orders, name='market_orders'),
]
