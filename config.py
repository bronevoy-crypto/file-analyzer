"""
КОНФИГУРАЦИЯ ПРИЛОЖЕНИЯ
Все настройки в одном месте
"""

import os
from pathlib import Path

# Пути
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# Создаем необходимые папки
for directory in [DATA_DIR, LOG_DIR]:
    directory.mkdir(exist_ok=True)

# Настройки анализа
DEFAULT_SETTINGS = {
    "max_analysis_time": 30,  # секунд
    "ignore_hidden": True,
    "min_file_size": 0,  # байт (0 = все файлы)
    "max_file_size": 1024 * 1024 * 100,  # 100 МБ
    "supported_extensions": [
        '.pdf', '.doc', '.docx', '.xls', '.xlsx',
        '.txt', '.jpg', '.png', '.zip', '.py'
    ]
}

# Настройки тегов
TAG_SETTINGS = {
    "min_tag_length": 2,
    "max_tag_length": 50,
    "stop_words": {
        'в', 'на', 'для', 'из', 'от', 'по', 'и', 'или', 'не',
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at'
    },
    "common_extensions": {
        '.pdf': 'документ',
        '.doc': 'документ',
        '.docx': 'документ',
        '.xlsx': 'таблица',
        '.jpg': 'изображение',
        '.png': 'изображение'
    }
}

# Настройки Excel
EXCEL_SETTINGS = {
    "default_output": "КаталогФайлов_с_тегами.xlsx",
    "backup_before_write": True,
    "auto_adjust_columns": True
}

# Настройки логирования
LOG_SETTINGS = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": LOG_DIR / "file_analyzer.log"
}

class Config:
    # Настройки вывода отчетов
    OUTPUT_STRATEGY = "PARENT_DIR"  # PARENT_DIR, SAME_DIR, CUSTOM
    
    # Можно задать кастомную папку для отчетов
    CUSTOM_OUTPUT_DIR = None  # Если None, будет использоваться стратегия выше
    
    @staticmethod
    def get_output_directory(target_dir):
        """Определяет директорию для сохранения отчета"""
        if Config.CUSTOM_OUTPUT_DIR:
            return Config.CUSTOM_OUTPUT_DIR
        
        if Config.OUTPUT_STRATEGY == "PARENT_DIR":
            parent = os.path.dirname(target_dir)
            return parent if parent else target_dir
        elif Config.OUTPUT_STRATEGY == "SAME_DIR":
            return target_dir
        
        return os.getcwd()  # По умолчанию текущая директория