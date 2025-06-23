import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Очистка и архивация старых логов'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Количество дней для хранения логов (по умолчанию: 30)',
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Сжимать старые логи вместо удаления',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать что будет сделано, но не выполнять действия',
        )

    def handle(self, *args, **options):
        logs_dir = settings.BASE_DIR / 'logs'
        
        if not logs_dir.exists():
            self.stdout.write(
                self.style.WARNING('Папка логов не найдена')
            )
            return
        
        cutoff_date = datetime.now() - timedelta(days=options['days'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Очистка логов старше {options["days"]} дней '
                f'(до {cutoff_date.strftime("%Y-%m-%d")})'
            )
        )
        
        log_files = list(logs_dir.glob('*.log*'))
        processed_count = 0
        
        for log_file in log_files:
            file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if file_time < cutoff_date:
                if options['dry_run']:
                    action = 'СЖАТЬ' if options['compress'] else 'УДАЛИТЬ'
                    self.stdout.write(f'{action}: {log_file.name}')
                else:
                    if options['compress']:
                        self.compress_log_file(log_file)
                        self.stdout.write(f'Сжат: {log_file.name}')
                    else:
                        log_file.unlink()
                        self.stdout.write(f'Удален: {log_file.name}')
                
                processed_count += 1
        
        if processed_count == 0:
            self.stdout.write('Нет файлов для обработки')
        else:
            action = 'обработано' if options['dry_run'] else 'очищено'
            self.stdout.write(
                self.style.SUCCESS(f'Файлов {action}: {processed_count}')
            )

    def compress_log_file(self, log_file):
        """Сжатие лог файла"""
        compressed_file = log_file.with_suffix(log_file.suffix + '.gz')
        
        with open(log_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Удаляем оригинальный файл после сжатия
        log_file.unlink()
