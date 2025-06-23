import json
from django.core.management.base import BaseCommand
from inventory.monitoring import SystemMonitor

class Command(BaseCommand):
    help = 'Проверка состояния системы и базы данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            choices=['json', 'text'],
            default='text',
            help='Формат вывода (json или text)',
        )
        parser.add_argument(
            '--alert',
            action='store_true',
            help='Отправлять уведомления при обнаружении проблем',
        )

    def handle(self, *args, **options):
        monitor = SystemMonitor()
        
        self.stdout.write(
            self.style.SUCCESS('Начинаем проверку состояния системы...')
        )
        
        # Проверка системы
        system_health = monitor.check_system_health()
        
        # Проверка базы данных
        db_health = monitor.check_database_health()
        
        # Проверка товаров с низким запасом
        low_stock_products = monitor.check_low_stock_products()
        
        # Формирование отчета
        report = {
            'system': system_health,
            'database': db_health,
            'low_stock_count': low_stock_products.count(),
            'low_stock_products': [
                {
                    'id': p.id,
                    'name': p.name,
                    'stock': p.stock_quantity
                } for p in low_stock_products[:10]
            ]
        }
        
        # Вывод в зависимости от формата
        if options['format'] == 'json':
            self.stdout.write(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            self.display_text_report(report)
        
        # Определение статуса
        if (system_health.get('cpu_usage', 0) > 90 or 
            system_health.get('memory_usage', 0) > 90 or
            db_health.get('status') != 'healthy' or
            low_stock_products.count() > 5):
            self.stdout.write(
                self.style.WARNING('⚠️  Обнаружены проблемы, требующие внимания')
            )
            return 1
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Система работает нормально')
            )
            return 0

    def display_text_report(self, report):
        """Отображение отчета в текстовом формате"""
        
        self.stdout.write(self.style.HTTP_INFO('\n=== ОТЧЕТ О СОСТОЯНИИ СИСТЕМЫ ==='))
        
        # Система
        system = report['system']
        self.stdout.write(f"\n🖥️  Система:")
        self.stdout.write(f"   CPU: {system.get('cpu_usage', 0):.1f}%")
        self.stdout.write(f"   Память: {system.get('memory_usage', 0):.1f}%")
        self.stdout.write(f"   Диск: {system.get('disk_usage', 0):.1f}%")
        
        # База данных
        db = report['database']
        status_color = self.style.SUCCESS if db.get('status') == 'healthy' else self.style.ERROR
        self.stdout.write(f"\n🗄️  База данных:")
        self.stdout.write(f"   Статус: {status_color(db.get('status', 'unknown'))}")
        if db.get('status') == 'healthy':
            self.stdout.write(f"   Товары: {db.get('products', 0)}")
            self.stdout.write(f"   Заказы: {db.get('orders', 0)}")
            self.stdout.write(f"   Клиенты: {db.get('customers', 0)}")
        
        # Низкие запасы
        low_stock_count = report['low_stock_count']
        self.stdout.write(f"\n📦 Товары с низким запасом: {low_stock_count}")
        
        if low_stock_count > 0:
            self.stdout.write("   Требуют внимания:")
            for product in report['low_stock_products']:
                self.stdout.write(
                    f"   - {product['name']}: {product['stock']} ед."
                )
        
        self.stdout.write(f"\n{'='*50}")
