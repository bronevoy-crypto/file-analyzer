"""
ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
Общие утилиты для всего проекта
"""

import os
import re
import hashlib
from datetime import datetime
from typing import List, Union, Optional
from pathlib import Path


def safe_path(path: Union[str, Path]) -> Path:
    """Безопасно создает Path объект"""
    return Path(path) if isinstance(path, str) else path


def format_size(size_bytes: int) -> str:
    """Форматирует размер файла в читаемый вид"""
    for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} ПБ"


def format_date(timestamp: float) -> str:
    """Форматирует дату"""
    return datetime.fromtimestamp(timestamp).strftime("%d.%m.%Y %H:%M:%S")


def calculate_hash(filepath: Union[str, Path], 
                  algorithm: str = "md5") -> str:
    """Вычисляет хеш файла"""
    hash_func = getattr(hashlib, algorithm, hashlib.md5)()
    
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception:
        return "ОШИБКА"


def clean_filename(filename: str) -> str:
    """Очищает имя файла от небезопасных символов"""
    # Удаляем небезопасные символы
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Ограничиваем длину
    return cleaned[:255]


def split_by_separators(text: str) -> List[str]:
    """Разбивает текст по различным разделителям"""
    if not text:
        return []
    
    # Заменяем все разделители на пробелы
    separators = ['_', '-', '.', ',', ';', '(', ')', '[', ']', '{', '}']
    for sep in separators:
        text = text.replace(sep, ' ')
    
    # Разбиваем на слова
    return [word.strip() for word in text.split() if word.strip()]


def is_valid_file(filepath: Union[str, Path], 
                 min_size: int = 0,
                 max_size: int = None,
                 extensions: List[str] = None) -> bool:
    """Проверяет, является ли файл валидным для анализа"""
    path = safe_path(filepath)
    
    # Проверка существования
    if not path.exists() or not path.is_file():
        return False
    
    # Проверка размера
    size = path.stat().st_size
    if size < min_size:
        return False
    if max_size and size > max_size:
        return False
    
    # Проверка расширения
    if extensions:
        ext = path.suffix.lower()
        if ext not in extensions:
            return False
    
    return True


def timer(func):
    """Декоратор для измерения времени выполнения"""
    import time
    
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} выполнен за {end_time - start_time:.2f} секунд")
        return result
    
    return wrapper


class ProgressBar:
    """Простой прогресс-бар для консоли"""
    
    def __init__(self, total: int, width: int = 50):
        self.total = total
        self.width = width
        self.current = 0
    
    def update(self, increment: int = 1):
        """Обновляет прогресс"""
        self.current += increment
        self._display()
    
    def _display(self):
        """Отображает прогресс-бар"""
        percent = self.current / self.total
        bars = int(self.width * percent)
        spaces = self.width - bars
        
        bar = "[" + "█" * bars + " " * spaces + "]"
        percent_display = f"{percent * 100:6.2f}%"
        
        print(f"\r{bar} {percent_display} ({self.current}/{self.total})", end="")
    
    def finish(self):
        """Завершает отображение прогресса"""
        print()  # Новая строка