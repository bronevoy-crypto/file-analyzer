"""
МОДЕЛЬ: Сканер файлов
"""

import os
import hashlib
import time
from datetime import datetime
from typing import List, Dict, Optional


class FileScanner:
    """Сканирование файловой системы"""
    
    def __init__(self):
        self.errors = []
    
    def scan_directory(self, directory: str, 
                      max_seconds: int = 30) -> List[Dict]:
        """
        Сканирует директорию и возвращает информацию о файлах
        """
        results = []
        start_time = time.time()
        
        try:
            for root, dirs, files in os.walk(directory):
                # Игнорируем скрытые папки
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for filename in files:
                    # Проверяем лимит времени
                    if time.time() - start_time > max_seconds:
                        print(f"Достигнут лимит времени ({max_seconds}с)")
                        return results
                    
                    # Игнорируем скрытые файлы
                    if filename.startswith('.'):
                        continue
                    
                    full_path = os.path.join(root, filename)
                    
                    if not os.path.isfile(full_path):
                        continue
                    
                    # Анализируем файл
                    file_info = self._analyze_file(full_path, directory)
                    if file_info:
                        results.append(file_info)
            
            return results
            
        except Exception as e:
            self.errors.append(f"Ошибка сканирования: {str(e)}")
            return results
    
    def _analyze_file(self, full_path: str, 
                     base_directory: str) -> Optional[Dict]:
        """Анализирует один файл"""
        try:
            stat = os.stat(full_path)
            
            # Базовые метаданные
            filename = os.path.basename(full_path)
            rel_path = os.path.relpath(full_path, base_directory)
            
            try:
                created_date = datetime.fromtimestamp(os.path.getctime(full_path))
            except:
                created_date = datetime.fromtimestamp(stat.st_ctime)
            
            size_bytes = stat.st_size
            
            return {
                'full_path': full_path,
                'filename': filename,
                'relative_path': rel_path,
                'created_date': created_date,
                'size_bytes': size_bytes,
                'size_mb': round(size_bytes / (1024 * 1024), 2),
                'extension': os.path.splitext(filename)[1].lower(),
                'directory': base_directory
            }
            
        except Exception as e:
            self.errors.append(f"Ошибка анализа {full_path}: {str(e)}")
            return None
    
    def calculate_hash(self, filepath: str) -> str:
        """Вычисляет MD5 хеш файла"""
        try:
            hash_md5 = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.errors.append(f"Ошибка MD5 для {filepath}: {str(e)}")
            return "ОШИБКА"