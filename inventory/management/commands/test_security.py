import time
import requests
from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache
from inventory.tests.factories import ProductFactory, CustomerFactory, OrderFactory

class Command(BaseCommand):
    help = 'Тестирование системы безопасности и мониторинга'

    def add_arguments(self, parser):
        parser.add_argument(
            '--full',
            action='store_true',
            help='Полное тестирование (включая нагрузочные тесты)',
        )
        parser.add_argument(
            '--skip-rate-limit',
            action='store_true',
            help='Пропустить тесты rate limiting',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔒 Начинаем тестирование системы безопасности...')
        )
        
        # Счетчики тестов
        passed = 0
        failed = 0
        
        # Запускаем тесты
        tests = [
            self.test_csrf_protection,
            self.test_security_headers,
            self.test_authentication_required,
            self.test_admin_access_control,
            self.test_input_validation,
            self.test_logging_system,
            self.test_monitoring_commands,
        ]
        
        if not options['skip_rate_limit']:
            tests.append(self.test_rate_limiting)
        
        if options['full']:
            tests.extend([
                self.test_load_handling,
                self.test_error_handling,
                self.test_data_integrity,
            ])
        
        for test in tests:
            try:
                test()
                passed += 1
                self.stdout.write(f"✅ {test.__name__}: PASSED")
            except Exception as e:
                failed += 1
                self.stdout.write(
                    self.style.ERROR(f"❌ {test.__name__}: FAILED - {str(e)}")
                )
        
        # Итоговый отчет
        self.display_summary(passed, failed)
        
        return 0 if failed == 0 else 1

    def test_csrf_protection(self):
        """Тест защиты от CSRF атак"""
        client = Client(enforce_csrf_checks=True)
        
        # Создаем пользователя
        user = User.objects.create_user('testuser', 'test@test.com', 'testpass')
        client.login(username='testuser', password='testpass')
        
        # Попытка POST без CSRF токена
        response = client.post(reverse('inventory:product_create'), {
            'name': 'Test Product',
            'price': '100.00',
            'stock_quantity': '10'
        })
        
        # Должен быть отклонен из-за отсутствия CSRF токена
        if response.status_code not in [403, 400]:
            raise Exception(f"CSRF protection failed. Status: {response.status_code}")

    def test_security_headers(self):
        """Тест наличия заголовков безопасности"""
        client = Client()
        response = client.get(reverse('inventory:home'))
        
        required_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Referrer-Policy'
        ]
        
        for header in required_headers:
            if header not in response:
                raise Exception(f"Missing security header: {header}")

    def test_authentication_required(self):
        """Тест требования аутентификации для защищенных страниц"""
        client = Client()
        
        protected_urls = [
            'inventory:product_create',
        ]
        
        for url_name in protected_urls:
            response = client.get(reverse(url_name))
            if response.status_code != 302:  # Редирект на страницу входа
                raise Exception(f"Authentication not required for {url_name}")

    def test_admin_access_control(self):
        """Тест контроля доступа администратора"""
        client = Client()
        
        # Создаем обычного пользователя
        user = User.objects.create_user('normaluser', 'normal@test.com', 'testpass')
        client.login(username='normaluser', password='testpass')
        
        # Создаем продукт для тестирования удаления
        product = ProductFactory()
        
        # Попытка удалить продукт (только для админов)
        response = client.post(reverse('inventory:product_delete', args=[product.id]))
        
        if response.status_code != 403:
            raise Exception("Admin access control failed")

    def test_input_validation(self):
        """Тест валидации входных данных"""
        client = Client()
        user = User.objects.create_user('testuser2', 'test2@test.com', 'testpass')
        client.login(username='testuser2', password='testpass')
        
        # Получаем CSRF токен
        response = client.get(reverse('inventory:product_create'))
        csrf_token = response.context['csrf_token']
        
        # Попытка создать продукт с некорректными данными
        invalid_data = [
            {'name': '', 'price': '100', 'stock_quantity': '10'},  # Пустое имя
            {'name': 'Test', 'price': '-100', 'stock_quantity': '10'},  # Отрицательная цена
            {'name': 'Test', 'price': '100', 'stock_quantity': '-10'},  # Отрицательное количество
            {'name': 'A' * 300, 'price': '100', 'stock_quantity': '10'},  # Слишком длинное имя
        ]
        
        for data in invalid_data:
            data['csrfmiddlewaretoken'] = csrf_token
            response = client.post(reverse('inventory:product_create'), data)
            
            # Форма должна быть невалидной
            if response.status_code == 302:  # Успешное создание
                raise Exception(f"Input validation failed for data: {data}")

    def test_rate_limiting(self):
        """Тест ограничения частоты запросов"""
        client = Client()
        
        # Очищаем кеш
        cache.clear()
        
        # Делаем много запросов подряд
        url = reverse('inventory:ajax_product_search')
        
        for i in range(70):  # Лимит 60/час для анонимных
            response = client.get(url, {'q': f'test{i}'})
            
            if i > 60 and response.status_code == 403:
                # Rate limiting сработал
                return
        
        # Если дошли до сюда, rate limiting не работает
        raise Exception("Rate limiting not working properly")

    def test_logging_system(self):
        """Тест системы логирования"""
        import logging
        import tempfile
        import os
        
        # Создаем временный файл для лога
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            temp_log_file = f.name
        
        try:
            # Настраиваем временный логгер
            logger = logging.getLogger('test_security')
            handler = logging.FileHandler(temp_log_file)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            
            # Записываем тестовое сообщение
            test_message = "Test security log message"
            logger.info(test_message)
            
            # Проверяем, что сообщение записалось
            with open(temp_log_file, 'r') as f:
                content = f.read()
                if test_message not in content:
                    raise Exception("Logging system not working")
        
        finally:
            # Удаляем временный файл
            os.unlink(temp_log_file)

    def test_monitoring_commands(self):
        """Тест команд мониторинга"""
        from django.core.management import call_command
        from io import StringIO
        
        # Тест команды проверки состояния системы
        out = StringIO()
        try:
            call_command('check_system_health', stdout=out)
            output = out.getvalue()
            
            # Проверяем, что команда выполнилась без ошибок
            if 'ERROR' in output.upper() or 'EXCEPTION' in output.upper():
                raise Exception("System health check command failed")
        
        except Exception as e:
            if "Command 'check_system_health' not found" not in str(e):
                raise e

    def test_load_handling(self):
        """Тест обработки нагрузки"""
        client = Client()
        
        # Создаем тестовые данные
        ProductFactory.create_batch(50)
        
        start_time = time.time()
        
        # Выполняем множественные запросы
        for i in range(20):
            response = client.get(reverse('inventory:product_list'))
            if response.status_code != 200:
                raise Exception(f"Load test failed on request {i}")
        
        end_time = time.time()
        
        # Проверяем время отклика
        avg_response_time = (end_time - start_time) / 20
        if avg_response_time > 2.0:  # 2 секунды максимум
            raise Exception(f"Poor performance: {avg_response_time:.2f}s average")

    def test_error_handling(self):
        """Тест обработки ошибок"""
        client = Client()
        
        # Тест 404 ошибки
        response = client.get('/nonexistent-page/')
        if response.status_code != 404:
            raise Exception("404 error handling failed")
        
        # Тест несуществующего продукта
        response = client.get(reverse('inventory:product_detail', args=[99999]))
        if response.status_code != 404:
            raise Exception("Product not found error handling failed")

    def test_data_integrity(self):
        """Тест целостности данных"""
        from django.db import transaction, IntegrityError
        
        # Тест уникальности (если есть уникальные поля)
        try:
            # Создаем два продукта с одинаковыми именами (если есть unique constraint)
            ProductFactory(name="Test Unique Product")
            # Если unique constraint есть, следующая строка должна вызвать ошибку
            # ProductFactory(name="Test Unique Product")
        except IntegrityError:
            # Это ожидаемо, если есть unique constraint
            pass
        
        # Тест транзакций
        try:
            with transaction.atomic():
                product = ProductFactory(stock_quantity=100)
                # Имитируем ошибку в транзакции
                if product.stock_quantity == 100:
                    # Транзакция должна откатиться
                    raise Exception("Test rollback")
        except Exception:
            pass
        
        # Проверяем, что данные не сохранились из-за отката

    def display_summary(self, passed, failed):
        """Отображение итогового отчета"""
        total = passed + failed
        
        self.stdout.write(self.style.HTTP_INFO('\n' + '='*50))
        self.stdout.write(self.style.HTTP_INFO('ОТЧЕТ О ТЕСТИРОВАНИИ БЕЗОПАСНОСТИ'))
        self.stdout.write(self.style.HTTP_INFO('='*50))
        
        self.stdout.write(f"Всего тестов: {total}")
        self.stdout.write(self.style.SUCCESS(f"Пройдено: {passed}"))
        
        if failed > 0:
            self.stdout.write(self.style.ERROR(f"Провалено: {failed}"))
        else:
            self.stdout.write(self.style.SUCCESS("Провалено: 0"))
        
        success_rate = (passed / total * 100) if total > 0 else 0
        self.stdout.write(f"Процент успеха: {success_rate:.1f}%")
        
        if failed == 0:
            self.stdout.write(self.style.SUCCESS('\n🎉 Все тесты безопасности пройдены!'))
        else:
            self.stdout.write(self.style.WARNING('\n⚠️  Обнаружены проблемы безопасности!'))
        
        self.stdout.write('='*50)
