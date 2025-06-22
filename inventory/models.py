from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('active', 'Активный'),
        ('processed', 'Обработан'),
        ('completed', 'Завершен'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    placed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')  # Новое поле

class InventoryLevel(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE)
    current_stock = models.IntegerField()

    def __str__(self):
        return f"Stock for {self.product.name}"
