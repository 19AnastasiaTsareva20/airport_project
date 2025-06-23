from django.shortcuts import render
from .models import Product, Customer, Order, InventoryLevel
from django.db.models import Avg, Sum  # Для агрегации данных
from rest_framework import viewsets  # Для API ViewSet
from .serializers import ProductSerializer, CustomerSerializer, OrderSerializer, InventoryLevelSerializer

# Веб-представления (functions)

# Главная страница
def home(request):
    total_products = Product.objects.count()
    active_orders = Order.objects.filter(status='active').count()
    return render(request, 'inventory/home.html', {
        'total_products': total_products, 
        'active_orders': active_orders
    })

# Список товаров
def product_list(request):
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort_by', 'name')
    products = Product.objects.filter(name__icontains=search_query).order_by(sort_by)
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
    inventory_levels = InventoryLevel.objects.select_related('product').all()
    total_inventory_items = inventory_levels.count()
    return render(request, 'inventory/inventory.html', {
        'inventory_levels': inventory_levels,
        'total_inventory_items': total_inventory_items
    })

# Страница отчётов
def report_page(request):
    # Более эффективный способ подсчета общих продаж
    total_sales = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0
    average_product_price = Product.objects.aggregate(avg_price=Avg('price'))['avg_price'] or 0
    
    return render(request, 'inventory/reports.html', {
        'total_sales': total_sales, 
        'average_product_price': round(average_product_price, 2)
    })

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
