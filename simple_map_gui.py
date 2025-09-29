#!/usr/bin/env python3
"""
Simple GUI with basic map visualization for OSM files.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import json
from pathlib import Path
import threading

class SimpleOSMGUI:
    """Simple OSM GUI with map visualization."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OSM Map Processor - Simple Version")
        self.root.geometry("1000x700")
        
        self.osm_file_path = None
        self.osm_data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Create main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Left panel
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='y', padx=(0, 10))
        
        # Right panel (map)
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        self.setup_controls(left_frame)
        self.setup_map(right_frame)
        
    def setup_controls(self, parent):
        """Setup control panel."""
        # File selection
        file_frame = ttk.LabelFrame(parent, text="File Selection", padding="10")
        file_frame.pack(fill='x', pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state='readonly', width=30)
        file_entry.pack(pady=(0, 5))
        
        ttk.Button(file_frame, text="Browse OSM File", command=self.browse_file).pack()
        ttk.Button(file_frame, text="Load File", command=self.load_file, style='Accent.TButton').pack(pady=(5, 0))
        
        # Status
        self.status_var = tk.StringVar(value="No file loaded")
        ttk.Label(file_frame, textvariable=self.status_var).pack(pady=(5, 0))
        
        # Display options
        display_frame = ttk.LabelFrame(parent, text="Display Options", padding="10")
        display_frame.pack(fill='x', pady=(0, 10))
        
        self.show_nodes = tk.BooleanVar(value=False)
        self.show_ways = tk.BooleanVar(value=True)
        self.show_buildings = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(display_frame, text="Show Nodes", variable=self.show_nodes, 
                       command=self.refresh_map).pack(anchor='w')
        ttk.Checkbutton(display_frame, text="Show Ways", variable=self.show_ways, 
                       command=self.refresh_map).pack(anchor='w')
        ttk.Checkbutton(display_frame, text="Show Buildings", variable=self.show_buildings, 
                       command=self.refresh_map).pack(anchor='w')
        
        # Statistics
        stats_frame = ttk.LabelFrame(parent, text="Statistics", padding="10")
        stats_frame.pack(fill='both', expand=True)
        
        self.stats_text = tk.Text(stats_frame, height=15, width=30, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(stats_frame, orient='vertical', command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=scrollbar.set)
        
        self.stats_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
    def setup_map(self, parent):
        """Setup map panel."""
        map_frame = ttk.LabelFrame(parent, text="Map Preview", padding="10")
        map_frame.pack(fill='both', expand=True)
        
        # Create canvas
        self.canvas = tk.Canvas(map_frame, width=600, height=500, bg='lightblue')
        self.canvas.pack(fill='both', expand=True)
        
        # Map controls
        controls = ttk.Frame(map_frame)
        controls.pack(fill='x', pady=(5, 0))
        
        ttk.Button(controls, text="Refresh Map", command=self.refresh_map).pack(side='left')
        ttk.Button(controls, text="Clear Map", command=self.clear_map).pack(side='left', padx=(5, 0))
        
        # Initial message
        self.canvas.create_text(300, 250, text="Select and load an OSM file to see the map", 
                              fill="gray", font=("Arial", 14))
        
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
    
    def load_file(self):
        """Load OSM file."""
        if not self.osm_file_path:
            messagebox.showerror("Error", "Please select an OSM file first")
            return
        
        def load_thread():
            try:
                self.status_var.set("Loading...")
                self.root.update()
                
                # Parse OSM file
                self.osm_data = self.parse_osm_file(self.osm_file_path)
                
                # Update statistics
                self.update_stats()
                
                # Draw map
                self.draw_map()
                
                self.status_var.set("File loaded successfully")
                
            except Exception as e:
                self.status_var.set("Error loading file")
                messagebox.showerror("Error", f"Failed to load OSM file: {e}")
        
        thread = threading.Thread(target=load_thread)
        thread.daemon = True
        thread.start()
    
    def parse_osm_file(self, file_path):
        """Parse OSM file."""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        data = {'nodes': {}, 'ways': {}}
        
        # Parse nodes
        for node in root.findall('node'):
            node_id = int(node.get('id'))
            lat = float(node.get('lat'))
            lon = float(node.get('lon'))
            
            tags = {}
            for tag in node.findall('tag'):
                key = tag.get('k')
                value = tag.get('v')
                if key and value:
                    tags[key] = value
            
            data['nodes'][node_id] = {'lat': lat, 'lon': lon, 'tags': tags}
        
        # Parse ways
        for way in root.findall('way'):
            way_id = int(way.get('id'))
            
            nodes = []
            for nd in way.findall('nd'):
                node_id = int(nd.get('ref'))
                if node_id in data['nodes']:
                    nodes.append(node_id)
            
            tags = {}
            for tag in way.findall('tag'):
                key = tag.get('k')
                value = tag.get('v')
                if key and value:
                    tags[key] = value
            
            if nodes:
                data['ways'][way_id] = {'nodes': nodes, 'tags': tags}
        
        return data
    
    def update_stats(self):
        """Update statistics display."""
        if not self.osm_data:
            return
        
        nodes = len(self.osm_data['nodes'])
        ways = len(self.osm_data['ways'])
        
        # Count way types
        buildings = 0
        roads = 0
        other = 0
        
        for way_data in self.osm_data['ways'].values():
            tags = way_data['tags']
            if 'building' in tags:
                buildings += 1
            elif 'highway' in tags:
                roads += 1
            else:
                other += 1
        
        # Calculate bounds
        if self.osm_data['nodes']:
            lats = [node['lat'] for node in self.osm_data['nodes'].values()]
            lons = [node['lon'] for node in self.osm_data['nodes'].values()]
            
            min_lat, max_lat = min(lats), max(lats)
            min_lon, max_lon = min(lons), max(lons)
            
            bounds_text = f"Bounds:\nMin: {min_lat:.4f}, {min_lon:.4f}\nMax: {max_lat:.4f}, {max_lon:.4f}\nSize: {max_lat-min_lat:.4f}° × {max_lon-min_lon:.4f}°"
        else:
            bounds_text = "No coordinate data"
        
        stats = f"""OSM File Statistics
{'='*30}

Basic Counts:
• Nodes: {nodes:,}
• Ways: {ways:,}

Way Types:
• Buildings: {buildings:,}
• Roads: {roads:,}
• Other: {other:,}

{bounds_text}

File Info:
• Size: {Path(self.osm_file_path).stat().st_size / 1024 / 1024:.2f} MB
• Path: {Path(self.osm_file_path).name}
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats)
        
        # Store bounds for map drawing
        if self.osm_data['nodes']:
            self.bounds = (min_lon, min_lat, max_lon, max_lat)
        else:
            self.bounds = None
    
    def latlon_to_pixel(self, lat, lon):
        """Convert lat/lon to pixel coordinates."""
        if not self.bounds:
            return None
        
        min_lon, min_lat, max_lon, max_lat = self.bounds
        
        # Add padding
        padding = 0.1
        lon_range = (max_lon - min_lon) * (1 + 2 * padding)
        lat_range = (max_lat - min_lat) * (1 + 2 * padding)
        
        if lon_range == 0 or lat_range == 0:
            return None
        
        # Get canvas size
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 600, 500
        
        # Convert to pixel coordinates
        x = ((lon - (min_lon - (max_lon - min_lon) * padding)) / lon_range) * canvas_width
        y = ((max_lat + (max_lat - min_lat) * padding - lat) / lat_range) * canvas_height
        
        return (int(x), int(y))
    
    def draw_map(self):
        """Draw the map."""
        if not self.osm_data or not self.bounds:
            return
        
        self.canvas.delete("all")
        
        # Draw ways
        if self.show_ways.get():
            for way_data in self.osm_data['ways'].values():
                nodes = way_data['nodes']
                if len(nodes) < 2:
                    continue
                
                # Determine color
                tags = way_data['tags']
                if 'building' in tags and self.show_buildings.get():
                    color = 'orange'
                    width = 2
                elif 'highway' in tags:
                    color = 'gray'
                    width = 1
                else:
                    color = 'black'
                    width = 1
                
                # Draw way
                points = []
                for node_id in nodes:
                    if node_id in self.osm_data['nodes']:
                        node = self.osm_data['nodes'][node_id]
                        pixel = self.latlon_to_pixel(node['lat'], node['lon'])
                        if pixel:
                            points.append(pixel)
                
                if len(points) >= 2:
                    self.canvas.create_line(points, fill=color, width=width)
        
        # Draw nodes
        if self.show_nodes.get():
            for node_data in self.osm_data['nodes'].values():
                pixel = self.latlon_to_pixel(node_data['lat'], node_data['lon'])
                if pixel:
                    x, y = pixel
                    self.canvas.create_oval(x-2, y-2, x+2, y+2, fill='blue', outline='blue')
        
        # Add title
        self.canvas.create_text(10, 10, text="OSM Map", anchor='nw', 
                              fill='black', font=('Arial', 12, 'bold'))
    
    def refresh_map(self):
        """Refresh the map."""
        if self.osm_data:
            self.draw_map()
    
    def clear_map(self):
        """Clear the map."""
        self.canvas.delete("all")
        self.canvas.create_text(300, 250, text="Map cleared", 
                              fill="gray", font=("Arial", 14))
    
    def run(self):
        """Run the application."""
        self.root.mainloop()

def main():
    """Main function."""
    app = SimpleOSMGUI()
    app.run()

if __name__ == "__main__":
    main()
