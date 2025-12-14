"""
CONTROLLER: Главный контроллер
Связывает Model и View, управляет потоком выполнения
"""

import os
import time
from datetime import datetime
from typing import List, Dict

# Импортируем Model
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.file_scanner import FileScanner
from model.tag_engine import SmartTagEngine  
from model.excel_writer import ExcelWriter

# Импортируем View
from view.cli_view import CLIView


class MainController:
    """Главный контроллер приложения"""
    
    def __init__(self):
        # Инициализируем компоненты MVC
        self.view = CLIView()
        self.file_scanner = FileScanner()
        self.tag_engine = SmartTagEngine(
            min_frequency=0.15,  # 15% минимальная частота
            history_file="tag_history.json"
        )
        self.excel_writer = ExcelWriter()
        
        # Статистика
        self.stats = {
            'files_processed': 0,
            'total_tags': 0,
            'start_time': None,
            'end_time': None
        }
    
    def run(self):
        """Основной метод запуска приложения"""
        # 1. VIEW: Показываем приветствие
        self.view.show_welcome()
        
        # 2. VIEW: Запрашиваем директорию
        directory = self.view.get_directory_input()
        
        if not os.path.exists(directory):
            self.view.show_error(f"Директория не существует: {directory}")
            return False
        
        # 3. CONTROLLER: Начинаем анализ
        self.stats['start_time'] = datetime.now()
        
        # 4. VIEW: Показываем начало работы
        self.view.show_progress(0, 0, f"Начинаю анализ папки: {directory}")
        
        # 5. MODEL: Сканируем файлы
        files_data = self.file_scanner.scan_directory(directory)
        
        if not files_data:
            self.view.show_error("Файлы не найдены")
            return False
        
       
        # 6. MODEL: Умная пакетная обработка тегов
        all_files_with_tags = []
        all_tags_explanations = []
        self.view.show_progress(0, 0, "Анализирую частотность тегов...")
        
        files_with_tags, tag_stats = self.tag_engine.analyze_batch(files_data)
        
        # Показываем статистику тегов
        print(f"\n📊 Статистика тегов:")
        print(f"  Всего уникальных тегов: {tag_stats['total_tags']}")
        print(f"  Частые теги: {tag_stats['common_tags']}")
        print(f"  Категоризированные теги: {tag_stats['category_tags']}")
        
        # Показываем топ-10 тегов
        if tag_stats['tag_info']:
            print(f"\n🏆 Топ тегов:")
            sorted_tags = sorted(
                tag_stats['tag_info'].items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:10]
            
            for tag, info in sorted_tags:
                freq_percent = info['frequency'] * 100
                print(f"  {tag}: {info['count']} файлов ({freq_percent:.1f}%)")
        
        # 7. MODEL: Сохраняем в Excel
        excel_file = "КаталогФайлов_с_тегами.xlsx"
        
        success = self.excel_writer.save_results(
            files_data=files_with_tags,               # Используйте реальные данные
            tags_explanations=all_tags_explanations,  # Всё равно пустой, нужно создать
            output_file=excel_file,
            stats=self.stats
        )
        
        # 8. Завершаем
        self.stats['end_time'] = datetime.now()
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        self.stats['duration_seconds'] = round(duration, 2)
        
        # 9. VIEW: Показываем итоги
        summary = {
            'Файлов обработано': self.stats['files_processed'],
            'Всего тегов': self.stats['total_tags'],
            'Среднее тегов на файл': round(self.stats['total_tags'] / max(1, self.stats['files_processed']), 1),
            'Время выполнения': f"{self.stats['duration_seconds']} сек",
            'Файл результатов': excel_file
        }
        
        self.view.show_summary(summary)
        
        if success:
            self.view.show_success(f"Анализ завершен! Результаты сохранены в {excel_file}")
            return True
        else:
            self.view.show_error("Ошибка при сохранении результатов")
            return False


# Точка входа для тестирования контроллера
if __name__ == "__main__":
    controller = MainController()
    success = controller.run()
    
    if success:
        print("\n🎉 Готово! MVP с MVC архитектурой работает!")
    else:
        print("\n⚠️ Завершено с ошибками")