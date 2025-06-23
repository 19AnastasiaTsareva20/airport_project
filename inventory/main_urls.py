from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('customers/', views.customer_list, name='customer_list'),
    path('orders/', views.order_list, name='order_list'),
    path('inventory/', views.inventory_page, name='inventory'),
    path('reports/', views.report_page, name='reports'),
    path('ajax/dashboard-stats/', views.ajax_dashboard_stats, name='ajax_dashboard_stats'),
]
