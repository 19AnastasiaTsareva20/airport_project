import functools
import logging
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django_ratelimit.decorators import ratelimit

security_logger = logging.getLogger('security')

def secure_view(view_func):
    """
    Декоратор для обеспечения безопасности представлений
    """
    @functools.wraps(view_func)
    @csrf_protect
    @never_cache
    def wrapper(request, *args, **kwargs):
        # Логируем доступ к защищенному представлению
        security_logger.info(
            f'Access to secure view {view_func.__name__} from IP {get_client_ip(request)}'
        )
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    """
    Декоратор для проверки прав администратора
    """
    @functools.wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            security_logger.warning(
                f'Unauthorized access attempt to admin view by user {request.user.username} '
                f'from IP {get_client_ip(request)}'
            )
            return HttpResponseForbidden('Access denied')
        return view_func(request, *args, **kwargs)
    return wrapper

def rate_limited_view(rate='10/m'):
    """
    Декоратор для ограничения частоты запросов
    """
    def decorator(view_func):
        @functools.wraps(view_func)
        @ratelimit(key='ip', rate=rate, method='ALL')
        def wrapper(request, *args, **kwargs):
            if getattr(request, 'limited', False):
                security_logger.warning(
                    f'Rate limit exceeded for view {view_func.__name__} '
                    f'from IP {get_client_ip(request)}'
                )
                return HttpResponseForbidden('Rate limit exceeded')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def get_client_ip(request):
    """Получение IP адреса клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
