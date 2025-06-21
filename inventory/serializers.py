from rest_framework import serializers
from .models import Product, Order

class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для модели товара."""
    class Meta:
        model = Product
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для модели заказа."""
    class Meta:
        model = Order
        fields = '__all__'
