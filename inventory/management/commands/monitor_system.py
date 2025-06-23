# inventory/management/commands/monitor_system.py
import time
import json
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from io import StringIO
from inventory.monitoring import SystemMonitor

class Command(BaseCommand):
    help = 'Комплексный мониторинг системы безопасности и производительности'

    def add_arguments(self, parser):
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Непрерывный мониторинг (запускается в цикле)',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=300,
            help='Интервал между проверками в секундах (по умолчанию: 300)',
        )
        parser.add_argument(
            '--log-file',
            type=str,
            help='Файл для записи логов мониторинга',
        )
        parser.add_argument(
            '--alert-threshold',
            type=int,
            default=80,
            help='Порог для отправки уведомлений (по умолчанию: 80%)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Запуск системы мониторинга...')
        )
        
        monitor = SystemMonitor()
        
        if options['continuous']:
            self.run_continuous_monitoring(monitor, options)
        else:
            self.run_single_check(monitor, options)

    def run_single_check(self, monitor, options):
        """Однократная проверка системы"""
        self.stdout.write('Выполняем комплексную проверку системы...')
        
        # 1. Проверка состояния системы
        self.stdout.write('\n1. Проверка системных ресурсов...')
        system_health = monitor.check_system_health()
        self.display_system_health(system_health, options['alert_threshold'])
        
        # 2. Проверка базы данных
        self.stdout.write('\n2. Проверка базы данных...')
        db_health = monitor.check_database_health()
        self.display_db_health(db_health)
        
        # 3. Проверка низких запасов
        self.stdout.write('\n3. Проверка запасов товаров...')
        low_stock = monitor.check_low_stock_products()
        self.display_stock_status(low_stock)
        
        # 4. Тестирование безопасности
        self.stdout.write('\n4. Быстрая проверка безопасности...')
        self.run_security_check()
        
        # 5. Проверка производительности
        self.stdout.write('\n5. Проверка производительности...')
        self.run_performance_check()
        
        # 6. Очистка логов
        self.stdout.write('\n6. Проверка размера логов...')
        self.check_log_size()
        
        # Сохранение отчета
        if options['log_file']:
            self.save_monitoring_report(options['log_file'], {
                'timestamp': datetime.now().isoformat(),
                'system_health': system_health,
                'db_health': db_health,
                'low_stock_count': low_stock.count(),
            })

    def run_continuous_monitoring(self, monitor, options):
        """Непрерывный мониторинг"""
        interval = options['interval']
        
        self.stdout.write(
            f'Запуск непрерывного мониторинга с интервалом {interval} секунд'
        )
        self.stdout.write('Для остановки нажмите Ctrl+C')
        
        try:
            while True:
                self.stdout.write(f'\n--- Проверка в {datetime.now().strftime("%H:%M:%S")} ---')
                
                # Быстрая проверка системы
                system_health = monitor.check_system_health()
                self.display_system_health(system_health, options['alert_threshold'])
                
                # Проверка критических показателей
                if (system_health.get('cpu_usage', 0) > options['alert_threshold'] or
                    system_health.get('memory_usage', 0) > options['alert_threshold']):
                    self.stdout.write(
                        self.style.ERROR('⚠️  КРИТИЧЕСКИЕ ПОКАЗАТЕЛИ СИСТЕМЫ!')
                    )
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('\nМониторинг остановлен пользователем'))

    def display_system_health(self, health_data, threshold):
        """Отображение состояния системы"""
        cpu = health_data.get('cpu_usage', 0)
        memory = health_data.get('memory_usage', 0)
        disk = health_data.get('disk_usage', 0)
        
        def get_status_style(value):
            if value > threshold:
                return self.style.ERROR
            elif value > threshold * 0.7:
                return self.style.WARNING
            else:
                return self.style.SUCCESS
        
        self.stdout.write(f"   CPU: {get_status_style(cpu)(f'{cpu:.1f}%')}")
        self.stdout.write(f"   Память: {get_status_style(memory)(f'{memory:.1f}%')}")
        self.stdout.write(f"   Диск: {get_status_style(disk)(f'{disk:.1f}%')}")

    def display_db_health(self, db_health):
        """Отображение состояния БД"""
        status = db_health.get('status', 'unknown')
        
        if status == 'healthy':
            self.stdout.write(self.style.SUCCESS(f"   Статус: {status}"))
            self.stdout.write(f"   Товары: {db_health.get('products', 0)}")
            self.stdout.write(f"   Заказы: {db_health.get('orders', 0)}")
            self.stdout.write(f"   Клиенты: {db_health.get('customers', 0)}")
        else:
            self.stdout.write(self.style.ERROR(f"   Статус: {status}"))
            error = db_health.get('error', 'Неизвестная ошибка')
            self.stdout.write(self.style.ERROR(f"   Ошибка: {error}"))

    def display_stock_status(self, low_stock_products):
        """Отображение состояния запасов"""
        count = low_stock_products.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS("   Все товары в достаточном количестве"))
        else:
            self.stdout.write(self.style.WARNING(f"   Товаров с низким запасом: {count}"))
            for product in low_stock_products[:5]:
                self.stdout.write(f"   - {product.name}: {product.stock_quantity}")

    def run_security_check(self):
        """Быстрая проверка безопасности"""
        try:
            out = StringIO()
            call_command('test_security', stdout=out, skip_rate_limit=True)
            output = out.getvalue()
            
            if 'FAILED' in output:
                self.stdout.write(self.style.WARNING("   Обнаружены проблемы безопасности"))
            else:
                self.stdout.write(self.style.SUCCESS("   Безопасность в порядке"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   Ошибка проверки безопасности: {e}"))

    def run_performance_check(self):
        """Быстрая проверка производительности"""
        try:
            out = StringIO()
            call_command('performance_monitor', duration=10, interval=5, stdout=out)
            output = out.getvalue()
            
            # Простой анализ вывода
            if 'WARNING' in output or 'ERROR' in output:
                self.stdout.write(self.style.WARNING("   Обнаружены проблемы производительности"))
            else:
                self.stdout.write(self.style.SUCCESS("   Производительность в норме"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   Ошибка проверки производительности: {e}"))

    def check_log_size(self):
        """Проверка размера логов"""
        logs_dir = settings.BASE_DIR / 'logs'
        
        if not logs_dir.exists():
            self.stdout.write("   Папка логов не найдена")
            return
        
        total_size = 0
        for log_file in logs_dir.glob('*.log'):
            total_size += log_file.stat().st_size
        
        # Конвертируем в MB
        size_mb = total_size / (1024 * 1024)
        
        if size_mb > 100:  # Больше 100 MB
            self.stdout.write(self.style.WARNING(f"   Размер логов: {size_mb:.1f} MB (рекомендуется очистка)"))
        else:
            self.stdout.write(self.style.SUCCESS(f"   Размер логов: {size_mb:.1f} MB"))

    def save_monitoring_report(self, filename, data):
        """Сохранение отчета мониторинга"""
        try:
            with open(filename, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
            
            self.stdout.write(f"Отчет сохранен в {filename}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Ошибка сохранения отчета: {e}"))
