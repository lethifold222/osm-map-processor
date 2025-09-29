from __future__ import annotations
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from tkinter import scrolledtext
import threading
from pathlib import Path
import json
from typing import Dict, Any, Optional

from config import AppConfig
from osm_pipeline import run_pipeline
from map_styles import MapStyleManager
from layer_controller import LayerController
from io import load_osm_cached
from layers import extract_layers

class OSMMapGUI:
    """Graphical User Interface for OSM Map Processing."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OSM Map Processor")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configuration
        self.config = AppConfig()
        self.style_manager = MapStyleManager()
        
        # Layer data
        self.layers_data = {}
        self.layer_controller = None
        
        # Variables
        self.osm_file_path = tk.StringVar()
        self.output_dir = tk.StringVar(value="./outputs")
        self.project_name = tk.StringVar(value="osm_project")
        
        # Layer selection variables
        self.layer_vars = {
            'roads': tk.BooleanVar(value=True),
            'buildings': tk.BooleanVar(value=True),
            'waterways': tk.BooleanVar(value=True),
            'amenities': tk.BooleanVar(value=True),
            'pois': tk.BooleanVar(value=True),
            'landuse': tk.BooleanVar(value=True)
        }
        
        # Style variables
        self.map_style = tk.StringVar(value="osm")
        self.background_color = tk.StringVar(value="#f5f5f3")
        self.custom_colors = {}
        
        # Output format variables
        self.vector_formats = {
            'svg': tk.BooleanVar(value=True),
            'pdf': tk.BooleanVar(value=True),
            'eps': tk.BooleanVar(value=False)
        }
        
        self.geodata_formats = {
            'geojson': tk.BooleanVar(value=True),
            'geopackage': tk.BooleanVar(value=False),
            'parquet': tk.BooleanVar(value=False)
        }
        
        self.image_formats = {
            'png': tk.BooleanVar(value=True),
            'jpg': tk.BooleanVar(value=False)
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Create main notebook
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Input tab
        self.setup_input_tab(notebook)
        
        # Layers tab
        self.setup_layers_tab(notebook)
        
        # Style tab
        self.setup_style_tab(notebook)
        
        # Output tab
        self.setup_output_tab(notebook)
        
        # Layer Control tab
        self.setup_layer_control_tab(notebook)
        
        # Process tab
        self.setup_process_tab(notebook)
        
    def setup_input_tab(self, notebook):
        """Setup input configuration tab."""
        input_frame = ttk.Frame(notebook)
        notebook.add(input_frame, text="Input")
        
        # Project name
        ttk.Label(input_frame, text="Project Name:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.project_name, width=30).grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # OSM File selection
        ttk.Label(input_frame, text="OSM File:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        file_frame = ttk.Frame(input_frame)
        file_frame.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        file_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(file_frame, textvariable=self.osm_file_path, state='readonly').grid(row=0, column=0, sticky='ew', padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_osm_file).grid(row=0, column=1)
        
        # Output directory
        ttk.Label(input_frame, text="Output Directory:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        output_frame = ttk.Frame(input_frame)
        output_frame.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(output_frame, textvariable=self.output_dir).grid(row=0, column=0, sticky='ew', padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_dir).grid(row=0, column=1)
        
        # CRS selection
        ttk.Label(input_frame, text="Target CRS (EPSG):").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        crs_var = tk.StringVar(value="3857")
        crs_combo = ttk.Combobox(input_frame, textvariable=crs_var, values=["4326", "3857", "32633", "32634"])
        crs_combo.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        
        input_frame.columnconfigure(1, weight=1)
        
    def setup_layers_tab(self, notebook):
        """Setup layers configuration tab."""
        layers_frame = ttk.Frame(notebook)
        notebook.add(layers_frame, text="Layers")
        
        # Main layers
        main_frame = ttk.LabelFrame(layers_frame, text="Main Layers")
        main_frame.pack(fill='x', padx=5, pady=5)
        
        for i, (layer, var) in enumerate(self.layer_vars.items()):
            ttk.Checkbutton(main_frame, text=layer.title(), variable=var).grid(row=i//2, column=i%2, sticky='w', padx=5, pady=2)
        
        # Amenities selection
        amenities_frame = ttk.LabelFrame(layers_frame, text="Amenities")
        amenities_frame.pack(fill='x', padx=5, pady=5)
        
        amenities_list = ["school", "hospital", "restaurant", "bank", "atm", "pharmacy", "fuel", "parking"]
        self.amenity_vars = {}
        
        for i, amenity in enumerate(amenities_list):
            var = tk.BooleanVar(value=amenity in ["school", "hospital"])
            self.amenity_vars[amenity] = var
            ttk.Checkbutton(amenities_frame, text=amenity.title(), variable=var).grid(row=i//4, column=i%4, sticky='w', padx=5, pady=2)
        
        # Landuse selection
        landuse_frame = ttk.LabelFrame(layers_frame, text="Landuse Types")
        landuse_frame.pack(fill='x', padx=5, pady=5)
        
        landuse_list = ["residential", "commercial", "industrial", "park", "forest", "grass", "farmland"]
        self.landuse_vars = {}
        
        for i, landuse in enumerate(landuse_list):
            var = tk.BooleanVar(value=landuse in ["residential", "commercial"])
            self.landuse_vars[landuse] = var
            ttk.Checkbutton(landuse_frame, text=landuse.title(), variable=var).grid(row=i//4, column=i%4, sticky='w', padx=5, pady=2)
        
    def setup_style_tab(self, notebook):
        """Setup style configuration tab."""
        style_frame = ttk.Frame(notebook)
        notebook.add(style_frame, text="Style")
        
        # Map style selection
        ttk.Label(style_frame, text="Map Style:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        style_combo = ttk.Combobox(style_frame, textvariable=self.map_style, values=["osm", "minimal", "custom"])
        style_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        style_combo.bind('<<ComboboxSelected>>', self.on_style_changed)
        
        # Background color
        bg_frame = ttk.Frame(style_frame)
        bg_frame.grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=5)
        bg_frame.columnconfigure(1, weight=1)
        
        ttk.Label(bg_frame, text="Background Color:").grid(row=0, column=0, sticky='w')
        ttk.Entry(bg_frame, textvariable=self.background_color, width=10).grid(row=0, column=1, sticky='w', padx=(5, 5))
        ttk.Button(bg_frame, text="Choose", command=self.choose_background_color).grid(row=0, column=2)
        
        # Custom colors frame
        self.custom_colors_frame = ttk.LabelFrame(style_frame, text="Custom Colors")
        self.custom_colors_frame.grid(row=2, column=0, columnspan=2, sticky='nsew', padx=5, pady=5)
        
        style_frame.columnconfigure(1, weight=1)
        style_frame.rowconfigure(2, weight=1)
        
        self.setup_custom_colors()
        
    def setup_custom_colors(self):
        """Setup custom colors section."""
        # Clear existing widgets
        for widget in self.custom_colors_frame.winfo_children():
            widget.destroy()
        
        # Common layer colors
        layer_colors = {
            'roads': ['motorway', 'primary', 'secondary', 'residential'],
            'buildings': ['buildings'],
            'waterways': ['river', 'stream', 'canal'],
            'landuse': ['residential', 'commercial', 'park'],
            'pois': ['school', 'hospital', 'restaurant', 'bank']
        }
        
        row = 0
        for layer_type, sublayers in layer_colors.items():
            ttk.Label(self.custom_colors_frame, text=f"{layer_type.title()}:", font=('TkDefaultFont', 9, 'bold')).grid(row=row, column=0, sticky='w', padx=5, pady=2)
            row += 1
            
            for i, sublayer in enumerate(sublayers):
                color_key = f"{layer_type}_{sublayer}"
                if color_key not in self.custom_colors:
                    self.custom_colors[color_key] = "#000000"
                
                ttk.Label(self.custom_colors_frame, text=f"  {sublayer}:").grid(row=row, column=0, sticky='w', padx=15, pady=1)
                
                color_frame = ttk.Frame(self.custom_colors_frame)
                color_frame.grid(row=row, column=1, sticky='w', padx=5, pady=1)
                
                color_var = tk.StringVar(value=self.custom_colors[color_key])
                color_entry = ttk.Entry(color_frame, textvariable=color_var, width=8)
                color_entry.grid(row=0, column=0)
                
                ttk.Button(color_frame, text="...", width=3, 
                          command=lambda key=color_key, var=color_var: self.choose_custom_color(key, var)).grid(row=0, column=1, padx=(2, 0))
                
                row += 1
            
            row += 1  # Extra space between layer types
        
    def setup_output_tab(self, notebook):
        """Setup output configuration tab."""
        output_frame = ttk.Frame(notebook)
        notebook.add(output_frame, text="Output")
        
        # Vector formats
        vector_frame = ttk.LabelFrame(output_frame, text="Vector Formats")
        vector_frame.pack(fill='x', padx=5, pady=5)
        
        for i, (format, var) in enumerate(self.vector_formats.items()):
            ttk.Checkbutton(vector_frame, text=format.upper(), variable=var).grid(row=0, column=i, sticky='w', padx=5, pady=2)
        
        # Raster formats
        raster_frame = ttk.LabelFrame(output_frame, text="Raster Formats")
        raster_frame.pack(fill='x', padx=5, pady=5)
        
        for i, (format, var) in enumerate(self.image_formats.items()):
            ttk.Checkbutton(raster_frame, text=format.upper(), variable=var).grid(row=0, column=i, sticky='w', padx=5, pady=2)
        
        # Geodata formats
        geodata_frame = ttk.LabelFrame(output_frame, text="Geodata Formats")
        geodata_frame.pack(fill='x', padx=5, pady=5)
        
        for i, (format, var) in enumerate(self.geodata_formats.items()):
            ttk.Checkbutton(geodata_frame, text=format.title(), variable=var).grid(row=0, column=i, sticky='w', padx=5, pady=2)
        
        # Additional options
        options_frame = ttk.LabelFrame(output_frame, text="Options")
        options_frame.pack(fill='x', padx=5, pady=5)
        
        self.generate_reports = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Generate Reports (CSV + Markdown)", variable=self.generate_reports).grid(row=0, column=0, sticky='w', padx=5, pady=2)
        
        self.enable_cache = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Enable Caching", variable=self.enable_cache).grid(row=1, column=0, sticky='w', padx=5, pady=2)
    
    def setup_layer_control_tab(self, notebook):
        """Setup interactive layer control tab."""
        layer_frame = ttk.Frame(notebook)
        notebook.add(layer_frame, text="Layer Control")
        
        # Top frame with load data button
        top_frame = ttk.Frame(layer_frame)
        top_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(top_frame, text="Load OSM Data", command=self.load_osm_data_for_preview).pack(side='left', padx=(0, 10))
        ttk.Button(top_frame, text="Refresh Preview", command=self.refresh_layer_preview).pack(side='left')
        
        # Status label
        self.layer_status_label = ttk.Label(top_frame, text="No OSM data loaded")
        self.layer_status_label.pack(side='right')
        
        # Layer controller frame (will be populated when data is loaded)
        self.layer_control_frame = ttk.Frame(layer_frame)
        self.layer_control_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Placeholder text
        placeholder = ttk.Label(self.layer_control_frame, 
                              text="Load OSM data to start interactive layer control",
                              font=('TkDefaultFont', 12))
        placeholder.pack(expand=True)
        
    def setup_process_tab(self, notebook):
        """Setup processing tab."""
        process_frame = ttk.Frame(notebook)
        notebook.add(process_frame, text="Process")
        
        # Process button
        process_btn = ttk.Button(process_frame, text="Generate Maps", command=self.start_processing, style='Accent.TButton')
        process_btn.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(process_frame, mode='indeterminate')
        self.progress.pack(fill='x', padx=20, pady=10)
        
        # Log area
        ttk.Label(process_frame, text="Processing Log:").pack(anchor='w', padx=20, pady=(20, 5))
        
        self.log_text = scrolledtext.ScrolledText(process_frame, height=15, state='disabled')
        self.log_text.pack(fill='both', expand=True, padx=20, pady=5)
        
        # Save/Load config buttons
        config_frame = ttk.Frame(process_frame)
        config_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(config_frame, text="Save Config", command=self.save_config).pack(side='left', padx=(0, 10))
        ttk.Button(config_frame, text="Load Config", command=self.load_config).pack(side='left')
        
    def browse_osm_file(self):
        """Browse for OSM file."""
        filename = filedialog.askopenfilename(
            title="Select OSM File",
            filetypes=[("OSM files", "*.osm"), ("All files", "*.*")]
        )
        if filename:
            self.osm_file_path.set(filename)
    
    def browse_output_dir(self):
        """Browse for output directory."""
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.output_dir.set(dirname)
    
    def choose_background_color(self):
        """Choose background color."""
        color = colorchooser.askcolor(color=self.background_color.get())[1]
        if color:
            self.background_color.set(color)
    
    def choose_custom_color(self, color_key: str, color_var: tk.StringVar):
        """Choose custom color for a layer."""
        color = colorchooser.askcolor(color=color_var.get())[1]
        if color:
            color_var.set(color)
            self.custom_colors[color_key] = color
    
    def on_style_changed(self, event):
        """Handle style selection change."""
        self.setup_custom_colors()
    
    def save_config(self):
        """Save configuration to file."""
        config_data = self.get_config_dict()
        filename = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'w') as f:
                    json.dump(config_data, f, indent=2)
                self.log(f"Configuration saved to {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save configuration: {e}")
    
    def load_config(self):
        """Load configuration from file."""
        filename = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r') as f:
                    config_data = json.load(f)
                self.set_config_dict(config_data)
                self.log(f"Configuration loaded from {filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get current configuration as dictionary."""
        return {
            'project_name': self.project_name.get(),
            'osm_file': self.osm_file_path.get(),
            'output_dir': self.output_dir.get(),
            'layers': {k: v.get() for k, v in self.layer_vars.items()},
            'amenities': [k for k, v in self.amenity_vars.items() if v.get()],
            'landuse': [k for k, v in self.landuse_vars.items() if v.get()],
            'map_style': self.map_style.get(),
            'background_color': self.background_color.get(),
            'custom_colors': self.custom_colors,
            'vector_formats': [k for k, v in self.vector_formats.items() if v.get()],
            'geodata_formats': [k for k, v in self.geodata_formats.items() if v.get()],
            'image_formats': [k for k, v in self.image_formats.items() if v.get()],
            'generate_reports': self.generate_reports.get(),
            'enable_cache': self.enable_cache.get()
        }
    
    def set_config_dict(self, config_data: Dict[str, Any]):
        """Set configuration from dictionary."""
        self.project_name.set(config_data.get('project_name', 'osm_project'))
        self.osm_file_path.set(config_data.get('osm_file', ''))
        self.output_dir.set(config_data.get('output_dir', './outputs'))
        
        # Set layer variables
        for layer, enabled in config_data.get('layers', {}).items():
            if layer in self.layer_vars:
                self.layer_vars[layer].set(enabled)
        
        # Set amenities
        for amenity in config_data.get('amenities', []):
            if amenity in self.amenity_vars:
                self.amenity_vars[amenity].set(True)
        
        # Set landuse
        for landuse in config_data.get('landuse', []):
            if landuse in self.landuse_vars:
                self.landuse_vars[landuse].set(True)
        
        # Set style
        self.map_style.set(config_data.get('map_style', 'osm'))
        self.background_color.set(config_data.get('background_color', '#f5f5f3'))
        self.custom_colors.update(config_data.get('custom_colors', {}))
        
        # Set formats
        for format_name in config_data.get('vector_formats', []):
            if format_name in self.vector_formats:
                self.vector_formats[format_name].set(True)
        
        for format_name in config_data.get('geodata_formats', []):
            if format_name in self.geodata_formats:
                self.geodata_formats[format_name].set(True)
        
        for format_name in config_data.get('image_formats', []):
            if format_name in self.image_formats:
                self.image_formats[format_name].set(True)
        
        self.generate_reports.set(config_data.get('generate_reports', True))
        self.enable_cache.set(config_data.get('enable_cache', True))
        
        # Refresh custom colors display
        self.setup_custom_colors()
    
    def log(self, message: str):
        """Add message to log."""
        self.log_text.config(state='normal')
        self.log_text.insert('end', f"{message}\n")
        self.log_text.config(state='disabled')
        self.log_text.see('end')
        self.root.update_idletasks()
    
    def start_processing(self):
        """Start processing in a separate thread."""
        if not self.osm_file_path.get():
            messagebox.showerror("Error", "Please select an OSM file")
            return
        
        # Start processing in thread
        thread = threading.Thread(target=self.process_osm_data)
        thread.daemon = True
        thread.start()
    
    def process_osm_data(self):
        """Process OSM data and generate maps."""
        try:
            self.progress.start()
            self.log("Starting OSM data processing...")
            
            # Create configuration from GUI
            config = self.create_config_from_gui()
            
            # Run pipeline
            self.log("Loading OSM data...")
            run_pipeline(config, verbose=True)
            
            self.log("Processing completed successfully!")
            self.log(f"Output files saved to: {self.output_dir.get()}")
            
            messagebox.showinfo("Success", "Map generation completed successfully!")
            
        except Exception as e:
            self.log(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Processing failed: {str(e)}")
        finally:
            self.progress.stop()
    
    def create_config_from_gui(self) -> AppConfig:
        """Create AppConfig from GUI settings."""
        # Get layer visibility and colors from controller if available
        layer_visibility = self.get_layer_visibility_state()
        layer_colors = self.get_layer_color_state()
        
        # Convert GUI settings to AppConfig
        config_data = {
            'project_name': self.project_name.get(),
            'input': {
                'osm_file': self.osm_file_path.get()
            },
            'output': {
                'output_dir': self.output_dir.get(),
                'vector_formats': [k for k, v in self.vector_formats.items() if v.get()],
                'geodata_formats': [k for k, v in self.geodata_formats.items() if v.get()],
                'image_formats': [k for k, v in self.image_formats.items() if v.get()],
                'enable_reports': self.generate_reports.get()
            },
            'layers': {
                'roads': self.layer_vars['roads'].get(),
                'buildings': self.layer_vars['buildings'].get(),
                'waterways': self.layer_vars['waterways'].get(),
                'amenities': [k for k, v in self.amenity_vars.items() if v.get()],
                'pois': ['bank', 'atm'],  # Default POIs
                'landuse': [k for k, v in self.landuse_vars.items() if v.get()]
            },
            'visualize': {
                'map_style': self.map_style.get(),
                'background_color': self.background_color.get(),
                'custom_colors': {**self.custom_colors, **layer_colors}  # Merge GUI and controller colors
            },
            'cache': {
                'enable_cache': self.enable_cache.get(),
                'cache_dir': '.cache',
                'cache_ttl_hours': 24
            }
        }
        
        return AppConfig(**config_data)
    
    def load_osm_data_for_preview(self):
        """Load OSM data for interactive preview."""
        if not self.osm_file_path.get():
            messagebox.showerror("Error", "Please select an OSM file first")
            return
        
        def load_data():
            try:
                self.layer_status_label.config(text="Loading OSM data...")
                self.root.update()
                
                # Load OSM data
                osm_bundle = load_osm_cached(
                    osm_file=self.osm_file_path.get(),
                    cache_enabled=self.enable_cache.get(),
                    cache_dir='.cache',
                    ttl_hours=24
                )
                
                # Extract layers
                layers = extract_layers(
                    osm_bundle, 
                    [k for k, v in self.amenity_vars.items() if v.get()],
                    ['bank', 'atm']  # Default POIs
                )
                
                # Convert to dictionary format for layer controller
                self.layers_data = {
                    'roads': layers.roads,
                    'buildings': layers.buildings,
                    'waterways': layers.waterways,
                    'amenities': layers.amenities,
                    'pois': layers.pois,
                    'landuse': layers.landuse
                }
                
                # Create layer controller
                self.create_layer_controller()
                
                self.layer_status_label.config(text=f"Loaded {sum(len(gdf) if gdf is not None else 0 for gdf in self.layers_data.values() if isinstance(gdf, dict) or hasattr(gdf, '__len__'))} features")
                
            except Exception as e:
                self.layer_status_label.config(text="Error loading data")
                messagebox.showerror("Error", f"Failed to load OSM data: {str(e)}")
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=load_data)
        thread.daemon = True
        thread.start()
    
    def create_layer_controller(self):
        """Create the layer controller widget."""
        # Clear existing controller
        if self.layer_controller:
            self.layer_controller.main_frame.destroy()
        
        # Clear placeholder
        for widget in self.layer_control_frame.winfo_children():
            widget.destroy()
        
        # Create new controller
        self.layer_controller = LayerController(self.layer_control_frame, self.layers_data)
        
        # Set callback for map updates
        self.layer_controller.set_map_update_callback(self.on_layer_preview_update)
    
    def refresh_layer_preview(self):
        """Refresh the layer preview."""
        if self.layer_controller:
            self.layer_controller.update_map()
    
    def on_layer_preview_update(self):
        """Callback when layer preview is updated."""
        # This can be used to update other parts of the UI if needed
        pass
    
    def get_layer_visibility_state(self) -> Dict[str, Any]:
        """Get current layer visibility state."""
        if self.layer_controller:
            return self.layer_controller.get_visibility_state()
        return {}
    
    def get_layer_color_state(self) -> Dict[str, str]:
        """Get current layer color state."""
        if self.layer_controller:
            return self.layer_controller.get_color_state()
        return {}
    
    def run(self):
        """Run the GUI application."""
        self.root.mainloop()

def main():
    """Main function to run the GUI."""
    app = OSMMapGUI()
    app.run()

if __name__ == "__main__":
    main()
