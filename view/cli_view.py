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
    
    def show_tag_statistics(self, stats: Dict):
        """Показывает статистику тегов"""
        print("\n" + "=" * 50)
        print("АНАЛИЗ ТЕГОВ")
        print("=" * 50)
        
        print(f"📈 Общая статистика:")
        print(f"  Файлов обработано: {stats.get('total_files', 0)}")
        print(f"  Всего тегов: {stats.get('total_tags', 0)}")
        print(f"  Частые теги (>15%): {stats.get('common_tags', 0)}")
        print(f"  Категоризированные: {stats.get('category_tags', 0)}")
        
        if 'tag_info' in stats and stats['tag_info']:
            print(f"\n🏷️  Детализация тегов:")
            
            # Группируем по типу
            common_tags = []
            category_tags = []
            
            for tag, info in stats['tag_info'].items():
                if info['type'] == 'common':
                    common_tags.append((tag, info['count'], info['frequency']))
                else:
                    category_tags.append((tag, info['count'], info['frequency']))
            
            if common_tags:
                print(f"\n  Частые теги:")
                for tag, count, freq in sorted(common_tags, key=lambda x: x[1], reverse=True)[:15]:
                    print(f"    {tag:20} {count:3} файлов ({freq*100:5.1f}%)")
            
            if category_tags:
                print(f"\n  Категории:")
                for tag, count, freq in sorted(category_tags, key=lambda x: x[1], reverse=True):
                    examples = stats['tag_info'][tag].get('examples', [])
                    example_str = ", ".join(examples[:3]) + ("..." if len(examples) > 3 else "")
                    print(f"    {tag:20} {count:3} файлов ← {example_str}")