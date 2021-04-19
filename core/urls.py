from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('groups/', views.group_list, name='group_list'),
    path('group/create/', views.GroupCreateView.as_view(), name='group_create'),
    path('group/<int:group_id>/', views.event_list, name='event_list'),
    path('group/<int:group_id>/event/create/', views.event_create, name='event_create'),
    path('event/<int:event_id>/markets/', views.markets, name='markets'),
    path('event/<int:event_id>/market/create/', views.MarketCreateView.as_view(), name='market_create'),
    path('event/<int:event_id>/market/orders/', views.get_market_orders, name='market_orders'),
    path('event/<int:event_id>/market/<int:pk>/update/', views.MarketUpdateView.as_view(), name='market_update'),
    path('event/<int:event_id>/accounts/', views.event_accounts, name='event_accounts'),
    path('order_delete/', views.order_delete, name='order_delete'),
]
