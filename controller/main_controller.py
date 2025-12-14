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
from model.tag_engine import TagEngine
from model.excel_writer import ExcelWriter

# Импортируем View
from view.cli_view import CLIView


class MainController:
    """Главный контроллер приложения"""
    
    def __init__(self):
        # Инициализируем компоненты MVC
        self.view = CLIView()
        self.file_scanner = FileScanner()
        self.tag_engine = TagEngine()
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
        
        # 6. Обрабатываем каждый файл
        all_files_with_tags = []
        all_tags_explanations = []
        
        for i, file_data in enumerate(files_data, 1):
            # VIEW: Показываем прогресс
            self.view.show_progress(i, len(files_data), 
                                  f"Обработка файлов...")
            
            # MODEL: Генерируем теги
            tags = self.tag_engine.generate_tags(
                file_data['filename'], 
                file_data['relative_path']
            )
            
            # MODEL: Создаем объяснения тегов
            explanations = self.tag_engine.create_tags_explanation(
                tags, 
                file_data['filename'], 
                file_data['relative_path']
            )
            
            # Обновляем данные файла
            file_data['tags'] = tags
            file_data['tags_count'] = len(tags)
            all_files_with_tags.append(file_data)
            all_tags_explanations.extend(explanations)
            
            # VIEW: Показываем информацию о файле (опционально)
            if i <= 5:  # Показываем только первые 5 файлов для примера
                self.view.show_file_info(file_data, tags)
            
            # Обновляем статистику
            self.stats['files_processed'] = i
            self.stats['total_tags'] += len(tags)
        
        # 7. MODEL: Сохраняем в Excel
        excel_file = "КаталогФайлов_с_тегами.xlsx"
        
        success = self.excel_writer.save_results(
            files_data=all_files_with_tags,
            tags_explanations=all_tags_explanations,
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