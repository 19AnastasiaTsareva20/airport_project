import logging
import psutil
import time
from django.core.mail import send_mail
from django.conf import settings
from django.core.management.base import BaseCommand
from inventory.models import Product, Order, Customer

logger = logging.getLogger('inventory')

class SystemMonitor:
    """Класс для мониторинга системы"""
    
    def __init__(self):
        self.logger = logging.getLogger('inventory')
    
    def check_system_health(self):
        """Проверка состояния системы"""
        health_data = {
            'timestamp': time.time(),
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
        }
        
        # Логируем состояние системы
        self.logger.info(f'System health check: {health_data}')
        
        # Проверяем критические значения
        if health_data['cpu_usage'] > 90:
            self.send_alert('High CPU usage', f"CPU usage: {health_data['cpu_usage']}%")
        
        if health_data['memory_usage'] > 90:
            self.send_alert('High memory usage', f"Memory usage: {health_data['memory_usage']}%")
        
        if health_data['disk_usage'] > 90:
            self.send_alert('High disk usage', f"Disk usage: {health_data['disk_usage']}%")
        
        return health_data
    
    def check_database_health(self):
        """Проверка состояния базы данных"""
        try:
            # Простые запросы для проверки доступности БД
            product_count = Product.objects.count()
            order_count = Order.objects.count()
            customer_count = Customer.objects.count()
            
            db_health = {
                'status': 'healthy',
                'products': product_count,
                'orders': order_count,
                'customers': customer_count,
            }
            
            self.logger.info(f'Database health check: {db_health}')
            return db_health
            
        except Exception as e:
            self.logger.error(f'Database health check failed: {str(e)}')
            self.send_alert('Database error', f'Database health check failed: {str(e)}')
            return {'status': 'unhealthy', 'error': str(e)}
    
    def check_low_stock_products(self):
        """Проверка товаров с низким запасом"""
        low_stock_products = Product.objects.filter(stock_quantity__lte=10)
        
        if low_stock_products.exists():
            message = f'Found {low_stock_products.count()} products with low stock:\n'
            for product in low_stock_products[:10]:  # Первые 10
                message += f'- {product.name}: {product.stock_quantity} units\n'
            
            self.logger.warning(f'Low stock alert: {low_stock_products.count()} products')
            self.send_alert('Low stock alert', message)
        
        return low_stock_products
    
    def send_alert(self, subject, message):
        """Отправка уведомлений об критических событиях"""
        try:
            if hasattr(settings, 'EMAIL_HOST_USER') and settings.EMAIL_HOST_USER:
                send_mail(
                    subject=f'[Airport Inventory] {subject}',
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=['admin@yourdomain.com'],  # Замените на ваш email
                    fail_silently=False,
                )
                self.logger.info(f'Alert sent: {subject}')
            else:
                self.logger.warning(f'Email not configured. Alert: {subject} - {message}')
        except Exception as e:
            self.logger.error(f'Failed to send alert: {str(e)}')

def log_user_action(user, action, details=''):
    """Функция для логирования действий пользователей"""
    logger = logging.getLogger('inventory')
    logger.info(f'User action: {user.username} - {action} - {details}')

def log_data_change(model_name, object_id, action, user=None, changes=None):
    """Функция для логирования изменений данных"""
    logger = logging.getLogger('inventory')
    
    log_message = f'Data change: {model_name} ID:{object_id} - {action}'
    if user:
        log_message += f' by {user.username}'
    if changes:
        log_message += f' - Changes: {changes}'
    
    logger.info(log_message)
