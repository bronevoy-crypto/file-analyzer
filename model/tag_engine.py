"""
МОДЕЛЬ: Умный генератор тегов с фильтрацией
"""

import os
import re
from collections import Counter
from typing import List, Dict, Tuple
import json


class SmartTagEngine:
    """Умный генератор тегов с анализом частотности"""
    
    def __init__(self, min_frequency: float = 0.1, history_file: str = "tag_history.json"):
        """
        min_frequency: минимальная частота для сохранения тега (0.1 = 10%)
        history_file: файл для сохранения истории тегов
        """
        self.stop_words = {'в', 'на', 'для', 'из', 'от', 'по', 'и', 'или', 'не'}
        self.min_frequency = min_frequency
        self.history_file = history_file
        
        # Загружаем историю тегов
        self.tag_history = self._load_history()
        
        # Категории для группировки уникальных тегов
        self.category_patterns = {
            'человек_фамилия': r'\b[А-ЯЁ][а-яё]{2,}(ов|ев|ин|ын|ский|цкий|кая|ая)\b',
            'год_xxxx': r'\b(19|20)\d{2}\b',
            'номер_документа': r'\b№?\s*\d{3,}\b',
            'статус_документа': r'\b(подписан|утвержден|согласован|черновик|итоговый)\b',
            'период': r'\b(Q[1-4]|квартал|полугодие|годовой|месячный)\b',
        }
    
    def _load_history(self) -> Dict:
        """Загружает историю тегов из файла"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {'total_files': 0, 'tag_counts': {}, 'file_examples': {}}
    
    def _save_history(self):
        """Сохраняет историю тегов в файл"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.tag_history, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def analyze_batch(self, files_data: List[Dict]) -> Tuple[List[Dict], Dict]:
        """
        Анализирует пакет файлов и возвращает УМНЫЕ теги
        Возвращает: (файлы с тегами, статистика тегов)
        """
        # 1. Сначала собираем ВСЕ потенциальные теги
        all_potential_tags = []
        for file_data in files_data:
            raw_tags = self._extract_raw_tags(
                file_data['filename'], 
                file_data['relative_path']
            )
            all_potential_tags.extend(raw_tags)
        
        # 2. Анализируем частотность
        tag_counter = Counter(all_potential_tags)
        total_files = len(files_data)
        
        # 3. Фильтруем теги по частоте
        smart_tags_info = {}
        for tag, count in tag_counter.items():
            frequency = count / total_files
            
            if frequency >= self.min_frequency:
                # Частый тег - оставляем как есть
                smart_tags_info[tag] = {
                    'frequency': frequency,
                    'count': count,
                    'type': 'common'
                }
            else:
                # Редкий тег - пытаемся категоризировать
                category = self._categorize_tag(tag)
                if category:
                    # Добавляем в категорию
                    if category not in smart_tags_info:
                        smart_tags_info[category] = {
                            'frequency': frequency,
                            'count': count,
                            'type': 'category',
                            'examples': [tag]
                        }
                    else:
                        smart_tags_info[category]['count'] += count
                        smart_tags_info[category]['examples'].append(tag)
                # else: отбрасываем совсем
        
        # 4. Применяем теги к файлам
        result_files = []
        for file_data in files_data:
            file_with_tags = self._apply_smart_tags(file_data, smart_tags_info)
            result_files.append(file_with_tags)
        
        # 5. Обновляем историю
        self._update_history(result_files)
        
        # 6. Возвращаем результат
        stats = {
            'total_tags': len(smart_tags_info),
            'common_tags': sum(1 for t in smart_tags_info.values() if t['type'] == 'common'),
            'category_tags': sum(1 for t in smart_tags_info.values() if t['type'] == 'category'),
            'tag_info': smart_tags_info
        }
        
        return result_files, stats
    
    def _extract_raw_tags(self, filename: str, filepath: str) -> List[str]:
        """Извлекает сырые теги (старая логика, но улучшенная)"""
        tags = []
        
        # Из имени файла
        name_without_ext = os.path.splitext(filename)[0]
        name_parts = self._split_into_parts(name_without_ext)
        tags.extend([p.lower() for p in name_parts if len(p) > 2])
        
        # Из пути (только последние 2 уровня)
        path_parts = filepath.split(os.sep)[-3:]  # Берем только последние уровни
        for part in path_parts:
            if part and part not in {'.', '..'}:
                part_tags = self._split_into_parts(part)
                tags.extend([p.lower() for p in part_tags if len(p) > 2])
        
        # Из расширения (только если не слишком распространенное)
        ext = os.path.splitext(filename)[1].lower()
        if ext and ext not in {'.txt', '.log', '.tmp'}:
            tags.append(f"расширение{ext}")
        
        return tags
    
    def _split_into_parts(self, text: str) -> List[str]:
        """Умное разделение текста на части"""
        if not text:
            return []
        
        # Заменяем разделители
        for sep in ['_', '-', '.', ' ', ';', ',']:
            text = text.replace(sep, '|')
        
        parts = [p.strip() for p in text.split('|') if p.strip()]
        
        # Фильтруем
        filtered = []
        for part in parts:
            part_lower = part.lower()
            if (len(part) > 2 and 
                part_lower not in self.stop_words and
                not part.isdigit() and  # Цифры обрабатываем отдельно
                not re.match(r'^\d+$', part)):
                filtered.append(part)
        
        return filtered
    
    def _categorize_tag(self, tag: str) -> str:
        """Определяет категорию для редкого тега"""
        for category, pattern in self.category_patterns.items():
            if re.search(pattern, tag, re.IGNORECASE):
                return category
        
        # Проверяем по словарю
        category_keywords = {
            'человек': ['иванов', 'петров', 'сидоров', 'васильев'],
            'проект': ['проект', 'project', 'программа'],
            'клиент': ['клиент', 'customer', 'заказчик'],
            'отчет': ['отчет', 'отчёт', 'report'],
            'договор': ['договор', 'контракт', 'соглашение'],
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in tag.lower() for keyword in keywords):
                return f"{category}_разное"
        
        return ""
    
    def _apply_smart_tags(self, file_data: Dict, smart_tags_info: Dict) -> Dict:
        """Применяет умные теги к конкретному файлу"""
        raw_tags = self._extract_raw_tags(
            file_data['filename'], 
            file_data['relative_path']
        )
        
        final_tags = []
        categories_used = set()
        
        for raw_tag in raw_tags:
            # Если тег частый - добавляем
            if raw_tag in smart_tags_info and smart_tags_info[raw_tag]['type'] == 'common':
                final_tags.append(raw_tag)
            
            # Если тег редкий - проверяем категорию
            else:
                category = self._categorize_tag(raw_tag)
                if category and category not in categories_used:
                    final_tags.append(category)
                    categories_used.add(category)
        
        # Добавляем тег "прочее" если мало тегов
        if len(final_tags) < 2 and raw_tags:
            final_tags.append("прочее")
        
        # Обновляем данные файла
        file_data['tags'] = final_tags
        file_data['raw_tags_count'] = len(raw_tags)
        file_data['smart_tags_count'] = len(final_tags)
        
        return file_data
    
    def _update_history(self, files_data: List[Dict]):
        """Обновляет историю тегов"""
        self.tag_history['total_files'] += len(files_data)
        
        for file_data in files_data:
            for tag in file_data.get('tags', []):
                if tag not in self.tag_history['tag_counts']:
                    self.tag_history['tag_counts'][tag] = 0
                    self.tag_history['file_examples'][tag] = file_data['filename']
                self.tag_history['tag_counts'][tag] += 1
        
        self._save_history()