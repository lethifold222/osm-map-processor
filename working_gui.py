#!/usr/bin/env python3
"""
Working GUI for OSM Map Processor with basic functionality.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
import threading

class SimpleOSMParser:
    """Simple OSM XML parser without heavy dependencies."""
    
    def __init__(self):
        self.nodes = {}
        self.ways = {}
        self.relations = {}
        
    def parse_file(self, osm_file_path: str) -> Dict[str, Any]:
        """Parse OSM file and return basic statistics."""
        try:
            tree = ET.parse(osm_file_path)
            root = tree.getroot()
            
            # Count elements
            node_count = len([e for e in root if e.tag == 'node'])
            way_count = len([e for e in root if e.tag == 'way'])
            relation_count = len([e for e in root if e.tag == 'relation'])
            
            # Get some sample data
            sample_data = {
                'nodes': node_count,
                'ways': way_count,
                'relations': relation_count,
                'total_elements': node_count + way_count + relation_count
            }
            
            # Extract some tags
            tags = set()
            for element in root:
                for child in element:
                    if child.tag == 'tag':
                        key = child.get('k')
                        if key:
                            tags.add(key)
            
            sample_data['unique_tags'] = len(tags)
            sample_data['sample_tags'] = sorted(list(tags))[:20]  # First 20 tags
            
            return sample_data
            
        except Exception as e:
            raise Exception(f"Error parsing OSM file: {e}")

class WorkingOSMGUI:
    """Working GUI for OSM processing."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OSM Map Processor - Working Version")
        self.root.geometry("800x600")
        
        self.osm_file_path = None
        self.osm_data = None
        self.parser = SimpleOSMParser()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # File selection tab
        self.setup_file_tab(notebook)
        
        # Analysis tab
        self.setup_analysis_tab(notebook)
        
        # Export tab
        self.setup_export_tab(notebook)
        
    def setup_file_tab(self, notebook):
        """Setup file selection tab."""
        file_frame = ttk.Frame(notebook)
        notebook.add(file_frame, text="📁 File Selection")
        
        # Title
        title_label = ttk.Label(file_frame, text="OSM File Processing", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # File selection
        file_group = ttk.LabelFrame(file_frame, text="Select OSM File", padding="10")
        file_group.pack(fill='x', padx=20, pady=10)
        
        file_frame_inner = ttk.Frame(file_group)
        file_frame_inner.pack(fill='x')
        file_frame_inner.columnconfigure(0, weight=1)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame_inner, textvariable=self.file_path_var, 
                              state='readonly')
        file_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        
        ttk.Button(file_frame_inner, text="Browse", 
                  command=self.browse_file).grid(row=0, column=1)
        
        # Load button
        ttk.Button(file_group, text="Load and Analyze OSM File", 
                  command=self.load_osm_file, style='Accent.TButton').pack(pady=10)
        
        # Status
        self.status_var = tk.StringVar(value="No file loaded")
        status_label = ttk.Label(file_group, textvariable=self.status_var)
        status_label.pack(pady=5)
        
    def setup_analysis_tab(self, notebook):
        """Setup analysis tab."""
        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text="📊 Analysis")
        
        # Title
        title_label = ttk.Label(analysis_frame, text="OSM Data Analysis", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Analysis results
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame, height=20)
        self.analysis_text.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Buttons
        button_frame = ttk.Frame(analysis_frame)
        button_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(button_frame, text="Refresh Analysis", 
                  command=self.refresh_analysis).pack(side='left')
        ttk.Button(button_frame, text="Export Analysis", 
                  command=self.export_analysis).pack(side='left', padx=(10, 0))
        
    def setup_export_tab(self, notebook):
        """Setup export tab."""
        export_frame = ttk.Frame(notebook)
        notebook.add(export_frame, text="💾 Export")
        
        # Title
        title_label = ttk.Label(export_frame, text="Export Options", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Export options
        options_frame = ttk.LabelFrame(export_frame, text="Export Formats", padding="10")
        options_frame.pack(fill='x', padx=20, pady=10)
        
        self.export_formats = {
            'json': tk.BooleanVar(value=True),
            'csv': tk.BooleanVar(value=True),
            'txt': tk.BooleanVar(value=True)
        }
        
        for i, (format_name, var) in enumerate(self.export_formats.items()):
            ttk.Checkbutton(options_frame, text=f"{format_name.upper()} format", 
                           variable=var).grid(row=0, column=i, sticky='w', padx=10)
        
        # Export directory
        dir_frame = ttk.LabelFrame(export_frame, text="Export Directory", padding="10")
        dir_frame.pack(fill='x', padx=20, pady=10)
        
        dir_frame_inner = ttk.Frame(dir_frame)
        dir_frame_inner.pack(fill='x')
        dir_frame_inner.columnconfigure(0, weight=1)
        
        self.export_dir_var = tk.StringVar(value="./exports")
        dir_entry = ttk.Entry(dir_frame_inner, textvariable=self.export_dir_var)
        dir_entry.grid(row=0, column=0, sticky='ew', padx=(0, 10))
        
        ttk.Button(dir_frame_inner, text="Browse", 
                  command=self.browse_export_dir).grid(row=0, column=1)
        
        # Export button
        ttk.Button(export_frame, text="Export Data", 
                  command=self.export_data, style='Accent.TButton').pack(pady=20)
        
        # Export log
        log_frame = ttk.LabelFrame(export_frame, text="Export Log", padding="10")
        log_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.export_log = scrolledtext.ScrolledText(log_frame, height=8)
        self.export_log.pack(fill='both', expand=True)
        
    def browse_file(self):
        """Browse for OSM file."""
        filename = filedialog.askopenfilename(
            title="Select OSM File",
            filetypes=[("OSM files", "*.osm"), ("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            self.osm_file_path = filename
            self.status_var.set(f"File selected: {Path(filename).name}")
    
    def load_osm_file(self):
        """Load and analyze OSM file."""
        if not self.osm_file_path:
            messagebox.showerror("Error", "Please select an OSM file first")
            return
        
        def load_in_thread():
            try:
                self.status_var.set("Loading OSM file...")
                self.root.update()
                
                # Parse OSM file
                self.osm_data = self.parser.parse_file(self.osm_file_path)
                
                # Update analysis
                self.update_analysis()
                
                self.status_var.set(f"File loaded: {self.osm_data['total_elements']} elements")
                
            except Exception as e:
                self.status_var.set("Error loading file")
                messagebox.showerror("Error", f"Failed to load OSM file: {e}")
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=load_in_thread)
        thread.daemon = True
        thread.start()
    
    def update_analysis(self):
        """Update analysis display."""
        if not self.osm_data:
            return
        
        analysis_text = f"""
OSM File Analysis Report
{'='*50}

📊 Basic Statistics:
• Total Nodes: {self.osm_data['nodes']:,}
• Total Ways: {self.osm_data['ways']:,}
• Total Relations: {self.osm_data['relations']:,}
• Total Elements: {self.osm_data['total_elements']:,}

🏷️ Tags Information:
• Unique Tags: {self.osm_data['unique_tags']:,}
• Sample Tags: {', '.join(self.osm_data['sample_tags'])}

📁 File Information:
• File Path: {self.osm_file_path}
• File Size: {Path(self.osm_file_path).stat().st_size / 1024 / 1024:.2f} MB

🔍 Data Quality:
• Node/Way Ratio: {self.osm_data['nodes'] / max(self.osm_data['ways'], 1):.2f}
• Way/Relation Ratio: {self.osm_data['ways'] / max(self.osm_data['relations'], 1):.2f}

💡 Recommendations:
• This appears to be a {'large' if self.osm_data['total_elements'] > 100000 else 'medium' if self.osm_data['total_elements'] > 10000 else 'small'} dataset
• {'Consider using filtering for better performance' if self.osm_data['total_elements'] > 50000 else 'Dataset size is suitable for full processing'}
• {'High tag diversity suggests rich data' if self.osm_data['unique_tags'] > 100 else 'Moderate tag diversity'}

{'='*50}
Analysis completed successfully!
"""
        
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(1.0, analysis_text)
    
    def refresh_analysis(self):
        """Refresh analysis display."""
        if self.osm_data:
            self.update_analysis()
        else:
            messagebox.showwarning("Warning", "No OSM data loaded")
    
    def export_analysis(self):
        """Export analysis to file."""
        if not self.osm_data:
            messagebox.showwarning("Warning", "No OSM data to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Analysis",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.analysis_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Analysis exported to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export: {e}")
    
    def browse_export_dir(self):
        """Browse for export directory."""
        dirname = filedialog.askdirectory(title="Select Export Directory")
        if dirname:
            self.export_dir_var.set(dirname)
    
    def export_data(self):
        """Export OSM data in selected formats."""
        if not self.osm_data:
            messagebox.showwarning("Warning", "No OSM data to export")
            return
        
        def export_in_thread():
            try:
                export_dir = Path(self.export_dir_var.get())
                export_dir.mkdir(parents=True, exist_ok=True)
                
                self.log_export(f"Starting export to {export_dir}")
                
                # Export JSON
                if self.export_formats['json'].get():
                    json_file = export_dir / "osm_analysis.json"
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(self.osm_data, f, indent=2, ensure_ascii=False)
                    self.log_export(f"✓ Exported JSON: {json_file}")
                
                # Export CSV
                if self.export_formats['csv'].get():
                    csv_file = export_dir / "osm_statistics.csv"
                    with open(csv_file, 'w', encoding='utf-8') as f:
                        f.write("Metric,Value\n")
                        f.write(f"Nodes,{self.osm_data['nodes']}\n")
                        f.write(f"Ways,{self.osm_data['ways']}\n")
                        f.write(f"Relations,{self.osm_data['relations']}\n")
                        f.write(f"Total Elements,{self.osm_data['total_elements']}\n")
                        f.write(f"Unique Tags,{self.osm_data['unique_tags']}\n")
                    self.log_export(f"✓ Exported CSV: {csv_file}")
                
                # Export TXT
                if self.export_formats['txt'].get():
                    txt_file = export_dir / "osm_analysis.txt"
                    with open(txt_file, 'w', encoding='utf-8') as f:
                        f.write(self.analysis_text.get(1.0, tk.END))
                    self.log_export(f"✓ Exported TXT: {txt_file}")
                
                self.log_export("🎉 Export completed successfully!")
                
            except Exception as e:
                self.log_export(f"❌ Export failed: {e}")
        
        # Clear log
        self.export_log.delete(1.0, tk.END)
        
        # Run export in thread
        thread = threading.Thread(target=export_in_thread)
        thread.daemon = True
        thread.start()
    
    def log_export(self, message: str):
        """Log export message."""
        self.export_log.insert(tk.END, f"{message}\n")
        self.export_log.see(tk.END)
        self.root.update_idletasks()
    
    def run(self):
        """Run the GUI application."""
        self.root.mainloop()

def main():
    """Main function."""
    app = WorkingOSMGUI()
    app.run()

if __name__ == "__main__":
    main()
