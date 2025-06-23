import time
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.db import connection
from django.test.utils import override_settings
from inventory.models import Product, Order, Customer

class Command(BaseCommand):
    help = 'Мониторинг производительности базы данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--duration',
            type=int,
            default=60,
            help='Длительность мониторинга в секундах (по умолчанию: 60)',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=10,
            help='Интервал между проверками в секундах (по умолчанию: 10)',
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Файл для сохранения результатов',
        )

    def handle(self, *args, **options):
        duration = options['duration']
        interval = options['interval']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Начинаем мониторинг производительности на {duration} секунд '
                f'с интервалом {interval} секунд'
            )
        )
        
        results = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            result = self.check_performance()
            results.append(result)
            
            self.display_performance_info(result)
            
            time.sleep(interval)
        
        # Сохранение результатов
        if options['output']:
            self.save_results(results, options['output'])
        
        # Сводка
        self.display_summary(results)

    def check_performance(self):
        """Проверка производительности"""
        start_time = time.time()
        
        # Выполняем различные запросы и измеряем время
        queries = {}
        
        # Простой SELECT
        query_start = time.time()
        Product.objects.count()
        queries['product_count'] = time.time() - query_start
        
        # SELECT с фильтром
        query_start = time.time()
        Product.objects.filter(stock_quantity__lt=10).count()
        queries['low_stock_count'] = time.time() - query_start
        
        # JOIN запрос
        query_start = time.time()
        Order.objects.select_related('customer').count()
        queries['order_with_customer'] = time.time() - query_start
        
        # Агрегация
        query_start = time.time()
        from django.db.models import Avg
        Product.objects.aggregate(avg_price=Avg('price'))
        queries['avg_price'] = time.time() - query_start
        
        # Информация о соединениях с БД
        db_queries = len(connection.queries)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_time': time.time() - start_time,
            'queries': queries,
            'db_queries_count': db_queries,
        }

    def display_performance_info(self, result):
        """Отображение информации о производительности"""
        timestamp = result['timestamp']
        total_time = result['total_time']
        
        self.stdout.write(f"\n[{timestamp}]")
        self.stdout.write(f"Общее время: {total_time:.3f}s")
        self.stdout.write(f"Запросов к БД: {result['db_queries_count']}")
        
        for query_name, query_time in result['queries'].items():
            color = self.style.SUCCESS if query_time < 0.1 else self.style.WARNING
            self.stdout.write(f"  {query_name}: {color(f'{query_time:.3f}s')}")

    def save_results(self, results, filename):
        """Сохранение результатов в файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'Результаты сохранены в {filename}')
        )

    def display_summary(self, results):
        """Отображение сводки"""
        if not results:
            return
        
        self.stdout.write(self.style.HTTP_INFO('\n=== СВОДКА ==='))
        
        # Средние значения
        avg_total_time = sum(r['total_time'] for r in results) / len(results)
        avg_db_queries = sum(r['db_queries_count'] for r in results) / len(results)
        
        self.stdout.write(f"Среднее общее время: {avg_total_time:.3f}s")
        self.stdout.write(f"Среднее количество запросов: {avg_db_queries:.1f}")
        
        # Средние времена запросов
        for query_name in results[0]['queries'].keys():
            avg_time = sum(r['queries'][query_name] for r in results) / len(results)
            max_time = max(r['queries'][query_name] for r in results)
            
            color = self.style.SUCCESS if avg_time < 0.1 else self.style.WARNING
            self.stdout.write(
                f"{query_name}: среднее {color(f'{avg_time:.3f}s')}, "
                f"максимум {max_time:.3f}s"
            )
