from django.contrib import admin
from .models import Product, Customer, Order, InventoryLevel

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock_quantity')  # корректные поля
    search_fields = ('name',)  # поиск по названию товара

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email')  # корректные поля

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_amount', 'placed_at')  # корректные поля
    list_filter = ('placed_at',)  # фильтр по дате размещения заказа

@admin.register(InventoryLevel)
class InventoryLevelAdmin(admin.ModelAdmin):
    list_display = ('product', 'current_stock')  # корректные поля
