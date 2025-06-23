import logging
import time
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from django.contrib.auth.signals import user_login_failed
from django.dispatch import receiver

# Настройка логгера безопасности
security_logger = logging.getLogger('security')

class SecurityMiddleware(MiddlewareMixin):
    """
    Кастомный middleware для дополнительной безопасности
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Обработка входящих запросов"""
        
        # Логируем подозрительные запросы
        self.log_suspicious_requests(request)
        
        # Проверяем rate limiting
        if self.is_rate_limited(request):
            security_logger.warning(
                f'Rate limit exceeded for IP {self.get_client_ip(request)} '
                f'on path {request.path}'
            )
            return HttpResponseForbidden('Too many requests')
        
        return None
    
    def process_response(self, request, response):
        """Обработка ответов"""
        
        # Добавляем дополнительные заголовки безопасности
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Логируем ошибки
        if response.status_code >= 400:
            security_logger.warning(
                f'HTTP {response.status_code} error for IP {self.get_client_ip(request)} '
                f'on path {request.path}'
            )
        
        return response
    
    def get_client_ip(self, request):
        """Получение IP адреса клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def log_suspicious_requests(self, request):
        """Логирование подозрительных запросов"""
        
        # Список подозрительных паттернов
        suspicious_patterns = [
            'admin', 'wp-admin', 'phpmyadmin', '.env', 'config',
            'backup', 'login.php', 'xmlrpc.php', 'wp-login'
        ]
        
        path = request.path.lower()
        for pattern in suspicious_patterns:
            if pattern in path:
                security_logger.warning(
                    f'Suspicious request from IP {self.get_client_ip(request)}: {request.path}'
                )
                break
    
    def is_rate_limited(self, request):
        """Простая проверка rate limiting"""
        ip = self.get_client_ip(request)
        cache_key = f'rate_limit_{ip}'
        
        # Получаем количество запросов за последнюю минуту
        requests_count = cache.get(cache_key, 0)
        
        # Лимит: 60 запросов в минуту
        if requests_count >= 60:
            return True
        
        # Увеличиваем счетчик
        cache.set(cache_key, requests_count + 1, 60)
        return False


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Логирование неудачных попыток входа"""
    ip = request.META.get('REMOTE_ADDR', 'Unknown')
    username = credentials.get('username', 'Unknown')
    
    security_logger.warning(
        f'Failed login attempt for user "{username}" from IP {ip}'
    )
