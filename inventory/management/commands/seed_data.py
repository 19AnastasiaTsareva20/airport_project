# inventory/management/commands/seed_data.py

from django.core.management.base import BaseCommand
from faker import Faker
from inventory.models import Product, Customer, Order, InventoryLevel

class Command(BaseCommand):
    help = 'Seed the database with fake data'

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Создание фиктивных товаров
        for _ in range(10):
            Product.objects.create(
                name=fake.word(),
                description=fake.sentence(),
                price=fake.random_int(min=10, max=100),
                stock_quantity=fake.random_int(min=1, max=100)
            )

        # Создание фиктивных заказчиков
        for _ in range(5):
            Customer.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=fake.email()
            )

        # Создание фиктивных заказов
        customers = Customer.objects.all()
        for _ in range(10):
            order = Order.objects.create(
                customer=fake.random_element(customers),
                total_amount=fake.random_int(min=100, max=1000),
                placed_at=fake.date_time_between(start_date="-30d", end_date="now")
            )
            order.products.set(Product.objects.order_by('?')[:fake.random_int(min=1, max=5)])

        # Создание фиктивных уровней инвентаризации
        for product in Product.objects.all():
            InventoryLevel.objects.create(
                product=product,
                current_stock=fake.random_int(min=1, max=100)
            )
