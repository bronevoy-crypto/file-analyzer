"""
МОДЕЛЬ: Генератор тегов
Чистая бизнес-логика, без интерфейса
"""

import os
import re
from typing import List, Dict


class TagEngine:
    """Генерация и управление тегами"""
    
    def __init__(self):
        # Простые правила для начала (можно потом расширять)
        self.stop_words = {'в', 'на', 'для', 'из', 'от', 'по', 'и', 'или', 'не'}
    
    def generate_tags(self, filename: str, filepath: str) -> List[str]:
        """
        Генерирует теги из имени файла и пути
        Возвращает список тегов
        """
        tags = []
        
        # 1. Теги из имени файла (разбиваем по разделителям)
        name_without_ext = os.path.splitext(filename)[0]
        name_tags = self._extract_from_text(name_without_ext)
        tags.extend(name_tags)
        
        # 2. Теги из пути (извлекаем названия папок)
        path_tags = self._extract_from_path(filepath)
        tags.extend(path_tags)
        
        # 3. Теги из расширения
        ext = os.path.splitext(filename)[1].lower()
        if ext:
            tags.append(f"расширение{ext}")
        
        # 4. Очищаем и уникализируем
        clean_tags = self._clean_tags(tags)
        
        return clean_tags
    
    def _extract_from_text(self, text: str) -> List[str]:
        """Извлекает слова из текста"""
        # Заменяем разделители на пробелы
        text_lower = text.lower()
        for separator in ['_', '-', '.', ',', ';']:
            text_lower = text_lower.replace(separator, ' ')
        
        # Разбиваем на слова
        words = re.findall(r'\b[a-zа-яё0-9]{2,}\b', text_lower)
        
        # Фильтруем стоп-слова и цифры
        filtered = []
        for word in words:
            if (word not in self.stop_words and 
                not word.isdigit() and 
                len(word) > 2):
                filtered.append(word)
        
        return filtered
    
    def _extract_from_path(self, filepath: str) -> List[str]:
        """Извлекает теги из пути к файлу"""
        tags = []
        
        # Разбиваем путь на части
        path_parts = filepath.split(os.sep)
        
        for part in path_parts:
            # Игнорируем текущую директорию и пустые части
            if part in {'.', '..', ''}:
                continue
            
            # Извлекаем слова из названия папки
            part_tags = self._extract_from_text(part)
            tags.extend(part_tags)
            
            # Также добавляем саму папку как тег (если не слишком длинная)
            clean_part = part.lower().strip()
            if (len(clean_part) > 2 and 
                len(clean_part) < 20 and 
                clean_part not in self.stop_words):
                tags.append(clean_part)
        
        return tags
    
    def _clean_tags(self, tags: List[str]) -> List[str]:
        """Очищает и уникализирует теги"""
        # Удаляем дубликаты, сохраняя порядок
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)
        
        return unique_tags
    
    def create_tags_explanation(self, tags: List[str], 
                               filename: str, 
                               filepath: str) -> List[Dict]:
        """
        Создает объяснения для тегов (для листа "Теги" в Excel)
        Возвращает список словарей с описанием каждого тега
        """
        explanations = []
        
        for tag in tags:
            explanation = {
                'тег': tag,
                'источник': '',
                'описание': '',
                'пример_файла': filename
            }
            
            # Определяем источник тега
            name_without_ext = os.path.splitext(filename)[0].lower()
            if tag in name_without_ext:
                explanation['источник'] = 'имя_файла'
                explanation['описание'] = f'Обнаружен в имени файла: {filename}'
            elif any(tag in part.lower() for part in filepath.split(os.sep)):
                explanation['источник'] = 'путь_к_файлу'
                explanation['описание'] = f'Обнаружен в пути к файлу: {filepath}'
            elif tag.startswith('расширение'):
                explanation['источник'] = 'расширение_файла'
                explanation['описание'] = f'Расширение файла: {filename}'
            else:
                explanation['источник'] = 'авто_определение'
                explanation['описание'] = f'Автоматически сгенерированный тег'
            
            explanations.append(explanation)
        
        return explanations


# Пример использования (для тестов)
if __name__ == "__main__":
    engine = TagEngine()
    
    test_cases = [
        ("Договор_Иванов_2023_подписан.pdf", "Клиенты/Активные/"),
        ("Отчет_продажи_Январь.xlsx", "Финансы/2024/"),
        ("Презентация_компании_Альфа.pptx", "Общее/")
    ]
    
    for filename, path in test_cases:
        tags = engine.generate_tags(filename, path)
        print(f"{filename} в {path}")
        print(f"  Теги: {tags}")
        print()