from django.shortcuts import render
from .models import Product, Customer, Order, InventoryLevel
from django.db.models import Avg  # Для агрегации данных
from rest_framework import viewsets  # Для API ViewSet
from .serializers import ProductSerializer, CustomerSerializer, OrderSerializer, InventoryLevelSerializer

# Веб-представления (functions)

# Главная страница
def home(request):
    total_products = Product.objects.count()
    active_orders = Order.objects.filter(status='active').count()
    return render(request, 'inventory/home.html', {'total_products': total_products, 'active_orders': active_orders})

# Список товаров
def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

# Список заказчиков
def customer_list(request):
    customers = Customer.objects.all()
    return render(request, 'inventory/customer_list.html', {'customers': customers})

# Список заказов
def order_list(request):
    orders = Order.objects.all()
    return render(request, 'inventory/order_list.html', {'orders': orders})

# Страница инвентаризации
def inventory_page(request):
    total_inventory_items = InventoryLevel.objects.count()
    return render(request, 'inventory/inventory.html', {'total_inventory_items': total_inventory_items})

# Страница отчётов
def report_page(request):
    total_sales = sum(order.total_amount for order in Order.objects.all())
    average_product_price = Product.objects.aggregate(avg_price=Avg('price'))['avg_price'] or 0
    return render(request, 'inventory/reports.html', {'total_sales': total_sales, 'average_product_price': average_product_price})

# API ViewSet (classes)

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class InventoryLevelViewSet(viewsets.ModelViewSet):
    queryset = InventoryLevel.objects.all()
    serializer_class = InventoryLevelSerializer
