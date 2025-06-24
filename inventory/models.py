from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    # Добавляем полезные поля для склада
    category = models.CharField(max_length=100, blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def is_in_stock(self):
        """Проверка наличия товара на складе"""
        return self.stock_quantity > 0
    
    def is_low_stock(self, threshold=10):
        """Проверка низкого остатка"""
        return self.stock_quantity <= threshold

    class Meta:
        ordering = ['name']


class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    # Добавляем дополнительные полезные поля
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ['last_name', 'first_name']


# НОВАЯ МОДЕЛЬ - Промежуточная для связи Order и Product
class OrderItem(models.Model):
    """Промежуточная модель для связи заказов и продуктов с количеством"""
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        unique_together = ['order', 'product']
        ordering = ['product__name']
    
    def get_total(self):
        """Общая стоимость этой позиции"""
        return self.quantity * self.price
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('processed', 'Обработан'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),  # Добавляем статус отмены
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    # УБИРАЕМ прямую связь с продуктами - теперь через OrderItem
    # products = models.ManyToManyField(Product)  # <- УДАЛЯЕМ ЭТУ СТРОКУ
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    placed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    # Добавляем дополнительные поля
    shipping_address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Заказ #{self.id} - {self.customer.full_name}"
    
    def get_total_from_items(self):
        """Вычисляет общую сумму из OrderItem"""
        return sum(item.get_total() for item in self.items.all())
    
    def get_items_count(self):
        """Количество позиций в заказе"""
        return self.items.count()
    
    def get_total_quantity(self):
        """Общее количество товаров в заказе"""
        return sum(item.quantity for item in self.items.all())

    class Meta:
        ordering = ['-placed_at']


class InventoryLevel(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    current_stock = models.IntegerField()
    # Добавляем полезные поля для управления складом
    min_stock_level = models.IntegerField(default=10, help_text="Минимальный уровень запасов")
    max_stock_level = models.IntegerField(default=1000, help_text="Максимальный уровень запасов")
    last_updated = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=100, blank=True, null=True, help_text="Местоположение на складе")

    def __str__(self):
        return f"Запас для {self.product.name}: {self.current_stock}"
    
    def needs_reorder(self):
        """Нужно ли пополнить запас"""
        return self.current_stock <= self.min_stock_level
    
    def is_overstocked(self):
        """Превышен ли максимальный запас"""
        return self.current_stock >= self.max_stock_level
    
    def stock_status(self):
        """Статус запаса"""
        if self.needs_reorder():
            return "low"
        elif self.is_overstocked():
            return "high"
        else:
            return "normal"

    class Meta:
        ordering = ['product__name']
        