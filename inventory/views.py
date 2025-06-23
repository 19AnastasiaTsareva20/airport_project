from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Product, Customer, Order, InventoryLevel
from .forms import ProductFilterForm, CustomerFilterForm, OrderFilterForm
from .utils import export_products_csv, export_products_excel, get_dashboard_stats
from django.db.models import Avg, Sum
from rest_framework import viewsets
from .serializers import ProductSerializer, CustomerSerializer, OrderSerializer, InventoryLevelSerializer

# Веб-представления (functions)

def home(request):
    """Расширенная главная страница с детальной аналитикой"""
    stats = get_dashboard_stats()
    return render(request, 'inventory/home.html', stats)

def product_list(request):
    """Улучшенный список товаров с фильтрацией и пагинацией"""
    form = ProductFilterForm(request.GET)
    products = Product.objects.all()
    
    if form.is_valid():
        # Поиск
        search = form.cleaned_data.get('search')
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # Фильтр по цене
        min_price = form.cleaned_data.get('min_price')
        if min_price:
            products = products.filter(price__gte=min_price)
            
        max_price = form.cleaned_data.get('max_price')
        if max_price:
            products = products.filter(price__lte=max_price)
        
        # Фильтр по количеству
        min_stock = form.cleaned_data.get('min_stock')
        if min_stock:
            products = products.filter(stock_quantity__gte=min_stock)
            
        max_stock = form.cleaned_data.get('max_stock')
        if max_stock:
            products = products.filter(stock_quantity__lte=max_stock)
        
        # Сортировка
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by:
            products = products.order_by(sort_by)
        else:
            products = products.order_by('name')
    
    # Обработка экспорта
    export_format = request.GET.get('export')
    if export_format == 'csv':
        return export_products_csv(products)
    elif export_format == 'excel':
        return export_products_excel(products)
    
    # Пагинация
    paginator = Paginator(products, 10)  # 10 товаров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory/product_list.html', {
        'form': form,
        'page_obj': page_obj,
        'products': page_obj,  # для совместимости
        'total_count': products.count()
    })

def customer_list(request):
    """Улучшенный список заказчиков с фильтрацией и пагинацией"""
    form = CustomerFilterForm(request.GET)
    customers = Customer.objects.all()
    
    if form.is_valid():
        # Поиск
        search = form.cleaned_data.get('search')
        if search:
            customers = customers.filter(
                Q(first_name__icontains=search) | 
                Q(last_name__icontains=search) | 
                Q(email__icontains=search)
            )
        
        # Сортировка
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by:
            customers = customers.order_by(sort_by)
        else:
            customers = customers.order_by('first_name')
    
    # Пагинация
    paginator = Paginator(customers, 15)  # 15 заказчиков на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory/customer_list.html', {
        'form': form,
        'page_obj': page_obj,
        'customers': page_obj,  # для совместимости
        'total_count': customers.count()
    })

def order_list(request):
    """Улучшенный список заказов с фильтрацией и пагинацией"""
    form = OrderFilterForm(request.GET)
    orders = Order.objects.select_related('customer').all()
    
    if form.is_valid():
        # Поиск по ID
        search = form.cleaned_data.get('search')
        if search:
            try:
                order_id = int(search)
                orders = orders.filter(id=order_id)
            except ValueError:
                orders = orders.none()
        
        # Фильтр по статусу
        status = form.cleaned_data.get('status')
        if status:
            orders = orders.filter(status=status)
        
        # Фильтр по дате
        date_from = form.cleaned_data.get('date_from')
        if date_from:
            orders = orders.filter(placed_at__gte=date_from)
            
        date_to = form.cleaned_data.get('date_to')
        if date_to:
            orders = orders.filter(placed_at__lte=date_to)
        
        # Сортировка
        sort_by = form.cleaned_data.get('sort_by')
        if sort_by:
            orders = orders.order_by(sort_by)
        else:
            orders = orders.order_by('-placed_at')
    
    # Пагинация
    paginator = Paginator(orders, 10)  # 10 заказов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'inventory/order_list.html', {
        'form': form,
        'page_obj': page_obj,
        'orders': page_obj,  # для совместимости
        'total_count': orders.count()
    })

def inventory_page(request):
    """Страница инвентаризации с предупреждениями"""
    inventory_levels = InventoryLevel.objects.select_related('product').all()
    total_inventory_items = inventory_levels.count()
    
    # Товары с низким запасом
    low_stock_threshold = 10
    low_stock_items = inventory_levels.filter(current_stock__lte=low_stock_threshold)
    
    return render(request, 'inventory/inventory.html', {
        'inventory_levels': inventory_levels,
        'total_inventory_items': total_inventory_items,
        'low_stock_items': low_stock_items,
        'low_stock_threshold': low_stock_threshold
    })

def report_page(request):
    """Расширенная страница отчетов"""
    stats = get_dashboard_stats()
    return render(request, 'inventory/reports.html', stats)

# AJAX представления для обновления данных
def ajax_dashboard_stats(request):
    """AJAX endpoint для обновления статистики на главной странице"""
    if request.is_ajax():
        stats = get_dashboard_stats()
        return JsonResponse(stats, safe=False)
    return JsonResponse({'error': 'Invalid request'}, status=400)

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
    