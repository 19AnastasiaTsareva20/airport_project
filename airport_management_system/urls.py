from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(('inventory.api_urls', 'inventory_api'))),  # пространство имён для API
    path('', include(('inventory.main_urls', 'inventory_main'))),  # пространство имён для основных маршрутов
]
