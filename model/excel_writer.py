"""
МОДЕЛЬ: Работа с Excel
"""

from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
from datetime import datetime
from typing import List, Dict
import os


class ExcelWriter:
    """Запись результатов в Excel"""
    
    def save_results(self, files_data: List[Dict], 
                    tags_explanations: List[Dict],
                    output_file: str,
                    stats: Dict) -> bool:
        """
        Сохраняет результаты анализа в Excel файл
        """
        try:
            # Создаем новую книгу
            wb = Workbook()
            
            # 1. Лист "Файлы"
            ws_files = wb.active
            ws_files.title = "Файлы"
            
            # Заголовки (добавляем колонку "Теги")
            headers = ["Имя файла", "Путь", "Дата создания", 
                      "Размер (МБ)", "Расширение", "Теги", "Кол-во тегов"]
            ws_files.append(headers)
            
            # Данные файлов
            for file_data in files_data:
                ws_files.append([
                    file_data['filename'],
                    file_data['relative_path'],
                    file_data['created_date'].strftime("%d.%m.%Y %H:%M"),
                    file_data['size_mb'],
                    file_data['extension'],
                    ", ".join(file_data.get('tags', [])),
                    file_data.get('tags_count', 0)
                ])
            
            # 2. Лист "Теги" (НОВЫЙ - для Issue #1)
            ws_tags = wb.create_sheet("Теги")
            tags_headers = ["Тег", "Источник", "Описание", "Пример файла", "Частота"]
            ws_tags.append(tags_headers)
            
            # Считаем частоту тегов
            tag_frequency = {}
            for explanation in tags_explanations:
                tag = explanation['тег']
                tag_frequency[tag] = tag_frequency.get(tag, 0) + 1
            
            # Данные тегов (уникальные)
            seen_tags = set()
            for explanation in tags_explanations:
                tag = explanation['тег']
                if tag not in seen_tags:
                    seen_tags.add(tag)
                    ws_tags.append([
                        tag,
                        explanation['источник'],
                        explanation['описание'],
                        explanation['пример_файла'],
                        tag_frequency[tag]
                    ])
            
            # 3. Лист "Сводка"
            ws_summary = wb.create_sheet("Сводка")
            ws_summary.append(["Параметр", "Значение"])
            ws_summary.append(["Дата анализа", datetime.now().strftime("%d.%m.%Y %H:%M")])
            ws_summary.append(["Всего файлов", stats.get('files_processed', 0)])
            ws_summary.append(["Всего тегов", stats.get('total_tags', 0)])
            ws_summary.append(["Время выполнения", f"{stats.get('duration_seconds', 0)} сек"])
            
            # Автонастройка ширины колонок
            for ws in [ws_files, ws_tags, ws_summary]:
                for column in ws.columns:
                    max_length = 0
                    column_letter = get_column_letter(column[0].column)
                    for cell in column:
                        try:
                            cell_length = len(str(cell.value))
                            if cell_length > max_length:
                                max_length = cell_length
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    ws.column_dimensions[column_letter].width = adjusted_width
            
            # Сохраняем файл
            wb.save(output_file)
            
            return True
            
        except Exception as e:
            print(f"Ошибка при сохранении в Excel: {e}")
            return False