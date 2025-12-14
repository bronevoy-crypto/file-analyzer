import os
from collections import Counter
from model.file_scanner import FileScanner
from model.tag_engine import TagEngine
from model.excel_writer import ExcelWriter
from utils.helpers import format_size, get_category
from datetime import datetime

class MainController:
    def __init__(self, view):
        self.view = view
        self.file_scanner = FileScanner()
        self.tag_engine = TagEngine()
        self.excel_writer = ExcelWriter()
    
    def analyze_directory(self, directory_path):
        """Основной метод анализа директории"""
        if not os.path.exists(directory_path):
            self.view.show_error(f"Directory not found: {directory_path}")
            return
        
        self.view.show_message(f"Starting analysis of: {directory_path}")
        self.view.show_message(f"Analysis started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Сканирование файлов
        files = self.file_scanner.scan_directory(directory_path)
        self.view.show_message(f"Found {len(files)} files")
        
        analysis_results = []
        
        # Обработка каждого файла
        for idx, filepath in enumerate(files, 1):
            try:
                file_data = self._process_file(filepath, directory_path)
                analysis_results.append(file_data)
                
                # Обновление прогресса
                if idx % 10 == 0:
                    self.view.show_progress(idx, len(files))
                    
            except Exception as e:
                self.view.show_warning(f"Error processing {filepath}: {str(e)}")
        
        # Генерация отчета Excel
        self._generate_report(analysis_results, directory_path)
        
        # Отображение результатов
        self._display_summary(analysis_results)
    
    def _process_file(self, filepath, base_dir):
        """Обработка одного файла"""
        stats = os.stat(filepath)
        
        # Относительный путь для отображения
        rel_path = os.path.relpath(filepath, base_dir)
        
        file_data = {
            'filename': os.path.basename(filepath),
            'path': rel_path,
            'full_path': filepath,
            'size': stats.st_size,
            'size_kb': round(stats.st_size / 1024, 2),
            'created': datetime.fromtimestamp(stats.st_ctime),
            'modified': datetime.fromtimestamp(stats.st_mtime),
            'extension': os.path.splitext(filepath)[1].lower(),
        }
        
        # Определение категории
        file_data['category'] = get_category(file_data['extension'])
        
        # Добавление тегов
        tags = self.tag_engine.get_tags(
            file_data['filename'],
            file_data['extension'],
            file_data['size']
        )
        file_data['tags'] = tags
        
        return file_data
    
    def _generate_report(self, analysis_results, target_directory):
        """Генерация Excel отчета"""
        self.view.show_message("\nGenerating Excel report...")
        
        for file_data in analysis_results:
            self.excel_writer.add_file_data(file_data)
        
        # Сохраняем Excel рядом с анализируемой папкой
        excel_path = self.excel_writer.save(target_directory, "report")
        
        self.view.show_message(f"Excel report saved to: {excel_path}")
        self.view.show_message(f"Report size: {os.path.getsize(excel_path) / 1024:.2f} KB")
    
    def _display_summary(self, analysis_results):
        """Отображение сводки по анализу"""
        if not analysis_results:
            self.view.show_message("No files to analyze")
            return
        
        total_size = sum(f['size'] for f in analysis_results)
        extensions = Counter(f['extension'] for f in analysis_results)
        
        self.view.show_message("\n=== ANALYSIS SUMMARY ===")
        self.view.show_message(f"Total files: {len(analysis_results)}")
        self.view.show_message(f"Total size: {format_size(total_size)}")
        self.view.show_message("\nFiles by extension:")
        for ext, count in extensions.most_common():
            self.view.show_message(f"  {ext or 'no extension'}: {count} files")
        
        # Распределение по категориям
        categories = Counter(f['category'] for f in analysis_results)
        self.view.show_message("\nFiles by category:")
        for category, count in categories.most_common():
            self.view.show_message(f"  {category}: {count} files")
        
        # Статистика по тегам
        all_tags = []
        for f in analysis_results:
            all_tags.extend(f['tags'])
        
        if all_tags:
            tag_counter = Counter(all_tags)
            self.view.show_message("\nMost common tags:")
            for tag, count in tag_counter.most_common(10):
                self.view.show_message(f"  {tag}: {count} files")