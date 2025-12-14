import os
import sys
from controller.main_controller import MainController
from view.cli_view import CLIView

def main():
    view = CLIView()
    controller = MainController(view)
    
    # Получаем директорию для анализа и опционально папку для вывода
    directory, output_dir = view.get_analysis_directory()
    
    # Проверяем существование директории
    if not os.path.exists(directory):
        view.show_error(f"Directory '{directory}' does not exist!")
        sys.exit(1)
    
    # Анализируем директорию
    controller.analyze_directory(directory)
    
    view.show_message("\nAnalysis completed successfully!")

if __name__ == "__main__":
    main()