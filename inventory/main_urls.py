from django.urls import path
from . import views

app_name = 'inventory'  # Пространство имён

urlpatterns = [
    path('', views.home, name='home'),  # главная страница
    path('products/', views.product_list, name='product_list'),  # список товаров
    path('customers/', views.customer_list, name='customer_list'),  # список заказчиков
    path('orders/', views.order_list, name='order_list'),  # список заказов
    path('inventory/', views.inventory_page, name='inventory'),  # страница инвентаризации
    path('reports/', views.report_page, name='reports'),  # страница отчётов
]
