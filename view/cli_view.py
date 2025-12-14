"""
VIEW: Консольный интерфейс
Только отображение, без логики обработки
"""

from typing import List, Dict
from datetime import datetime


class CLIView:
    """Консольный интерфейс пользователя"""
    
    def show_welcome(self):
        """Показывает приветственное сообщение"""
        print("=" * 50)
        print("Анализатор файлов с тегами (MVC Architecture)")
        print("=" * 50)
    
    def show_progress(self, current: int, total: int, message: str = ""):
        """Показывает прогресс"""
        if message:
            print(f"\n{message}")
        if total > 0:
            percent = (current / total) * 100
            print(f"Прогресс: {current}/{total} файлов ({percent:.1f}%)")
    
    def show_file_info(self, file_info: Dict, tags: List[str]):
        """Показывает информацию о файле"""
        print(f"\n📄 {file_info['filename']}")
        print(f"   Путь: {file_info['relative_path']}")
        print(f"   Размер: {file_info['size_mb']} МБ")
        print(f"   Теги: {', '.join(tags) if tags else 'нет'}")
    
    def show_summary(self, stats: Dict):
        """Показывает итоговую статистику"""
        print("\n" + "=" * 50)
        print("ИТОГОВАЯ СТАТИСТИКА")
        print("=" * 50)
        
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("=" * 50)
    
    def show_error(self, error_message: str):
        """Показывает сообщение об ошибке"""
        print(f"\n❌ Ошибка: {error_message}")
    
    def show_success(self, message: str):
        """Показывает сообщение об успехе"""
        print(f"\n✅ {message}")
    
    def ask_yes_no(self, question: str) -> bool:
        """Задает вопрос Да/Нет"""
        while True:
            response = input(f"\n{question} (y/n): ").lower().strip()
            if response in ['y', 'да']:
                return True
            elif response in ['n', 'нет']:
                return False
            else:
                print("Пожалуйста, введите 'y' или 'n'")
    
    def get_directory_input(self) -> str:
        """Запрашивает путь к директории"""
        default_dir = "."
        user_input = input(f"\nВведите путь к папке (Enter для текущей '{default_dir}'): ").strip()
        return user_input if user_input else default_dir