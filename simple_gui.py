#!/usr/bin/env python3
"""
Simplified GUI launcher for OSM Map Processor.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sys
import os
from pathlib import Path

def show_info():
    """Show information about the program."""
    info_window = tk.Toplevel()
    info_window.title("OSM Map Processor - Information")
    info_window.geometry("600x400")
    
    text = tk.Text(info_window, wrap=tk.WORD, padx=10, pady=10)
    text.pack(fill=tk.BOTH, expand=True)
    
    info_text = """
OSM Map Processor - Программа для обработки карт OpenStreetMap

🎯 Основные возможности:
• Загрузка OSM файлов (.osm)
• Интерактивное управление слоями карты
• Настройка цветов и стилей
• Экспорт в различные форматы (SVG, PDF, PNG, GeoJSON)
• Предварительный просмотр карт в реальном времени

📁 Структура проекта:
• app/osm_parser.py - Парсер OSM XML файлов
• app/layer_controller.py - Управление слоями
• app/map_styles.py - Система стилизации
• app/gui.py - Графический интерфейс
• app/reports.py - Генерация отчетов

🚀 Как использовать:
1. Выберите OSM файл
2. Настройте слои и цвета
3. Сгенерируйте карты

⚠️ Примечание:
Для полной функциональности требуется установка всех зависимостей.
Если программа не запускается, проверьте установку пакетов:
pip install -r requirements.txt
"""
    
    text.insert(tk.END, info_text)
    text.config(state=tk.DISABLED)

def open_file_dialog():
    """Open file dialog to select OSM file."""
    filename = filedialog.askopenfilename(
        title="Выберите OSM файл",
        filetypes=[("OSM files", "*.osm"), ("All files", "*.*")]
    )
    if filename:
        messagebox.showinfo("Файл выбран", f"Выбран файл: {filename}")
        # Здесь можно добавить обработку файла

def create_main_window():
    """Create the main GUI window."""
    root = tk.Tk()
    root.title("OSM Map Processor")
    root.geometry("500x400")
    root.resizable(True, True)
    
    # Main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = ttk.Label(main_frame, text="🗺️ OSM Map Processor", 
                           font=("Arial", 18, "bold"))
    title_label.pack(pady=(0, 20))
    
    # Description
    desc_label = ttk.Label(main_frame, 
                          text="Программа для обработки и визуализации карт OpenStreetMap",
                          font=("Arial", 10))
    desc_label.pack(pady=(0, 30))
    
    # Buttons frame
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill=tk.X, pady=10)
    
    # Select file button
    select_btn = ttk.Button(buttons_frame, text="📁 Выбрать OSM файл", 
                           command=open_file_dialog, width=20)
    select_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    # Info button
    info_btn = ttk.Button(buttons_frame, text="ℹ️ Информация", 
                         command=show_info, width=15)
    info_btn.pack(side=tk.LEFT)
    
    # Status frame
    status_frame = ttk.LabelFrame(main_frame, text="Статус", padding="10")
    status_frame.pack(fill=tk.X, pady=(30, 10))
    
    status_label = ttk.Label(status_frame, text="Готов к работе")
    status_label.pack()
    
    # Features frame
    features_frame = ttk.LabelFrame(main_frame, text="Возможности", padding="10")
    features_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    features_text = """
✅ Загрузка OSM файлов
✅ Интерактивное управление слоями
✅ Настройка цветов и стилей
✅ Экспорт в различные форматы
✅ Предварительный просмотр карт
✅ Генерация отчетов
"""
    
    features_label = ttk.Label(features_frame, text=features_text, 
                              font=("Courier", 9))
    features_label.pack(anchor=tk.W)
    
    # Footer
    footer_label = ttk.Label(main_frame, text="Для полной функциональности используйте: python -m app gui",
                            font=("Arial", 8), foreground="gray")
    footer_label.pack(side=tk.BOTTOM, pady=(20, 0))
    
    return root

def main():
    """Main function."""
    try:
        root = create_main_window()
        root.mainloop()
    except Exception as e:
        print(f"Error creating GUI: {e}")
        messagebox.showerror("Ошибка", f"Не удалось запустить GUI: {e}")

if __name__ == "__main__":
    main()
