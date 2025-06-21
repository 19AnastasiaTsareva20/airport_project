from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, OrderViewSet, CustomObtainAuthToken

router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'orders', OrderViewSet)

urlpatterns = [
    path('auth-token/', CustomObtainAuthToken.as_view()),  # маршрут для получения токена
    path('', include(router.urls)),  # маршруты для продуктов и заказов
]
