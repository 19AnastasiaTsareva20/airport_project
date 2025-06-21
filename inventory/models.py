from django.db import models

class Category(models.Model):
    """Модель категории товаров."""
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Product(models.Model):
    """Модель товара."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    """Модель инвентарного предмета."""
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f'{self.product.name} ({self.location})'

class Order(models.Model):
    """Модель заказа."""
    STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('processing', 'В обработке'),
        ('completed', 'Завершен'),
    ]
    products = models.ManyToManyField(Product)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    ordered_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Заказ #{self.pk}'
