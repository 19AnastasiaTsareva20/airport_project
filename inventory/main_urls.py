from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.home, name='home'),  # Главная страница
    path('products/', views.product_list, name='product_list'),  # Список товаров
    path('customers/', views.customer_list, name='customer_list'),  # Список заказчиков
    path('orders/', views.order_list, name='order_list'),  # Список заказов
    path('inventory/', views.inventory_page, name='inventory'),  # Страница инвентаризации
    path('reports/', views.report_page, name='reports'),  # Страница отчётов
]
