from django.urls import path
from .views import ProductViewSet, CustomerViewSet, OrderViewSet, InventoryLevelViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('customers', CustomerViewSet)
router.register('orders', OrderViewSet)
router.register('inventories', InventoryLevelViewSet)

urlpatterns = router.urls
