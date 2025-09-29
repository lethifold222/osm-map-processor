#!/usr/bin/env python3
"""
GUI with map visualization for OSM Map Processor.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
import threading
import math

class SimpleMapCanvas:
    """Simple map canvas for basic OSM visualization."""
    
    def __init__(self, parent, width=800, height=600):
        self.parent = parent
        self.width = width
        self.height = height
        
        # Create canvas
        self.canvas = tk.Canvas(parent, width=width, height=height, bg='white')
        self.canvas.pack(fill='both', expand=True)
        
        # Map data
        self.bounds = None  # (min_lon, min_lat, max_lon, max_lat)
        self.nodes = {}
        self.ways = {}
        self.relations = {}
        
        # Display settings
        self.show_nodes = tk.BooleanVar(value=False)
        self.show_ways = tk.BooleanVar(value=True)
        self.show_buildings = tk.BooleanVar(value=True)
        self.show_roads = tk.BooleanVar(value=True)
        
        # Colors
        self.colors = {
            'node': '#0000FF',
            'way': '#000000',
            'building': '#FFA500',
            'road': '#666666',
            'water': '#0080FF',
            'background': '#F0F8FF'
        }
        
        self.canvas.config(bg=self.colors['background'])
        
    def calculate_bounds(self, osm_data):
        """Calculate map bounds from OSM data."""
        if not osm_data.get('nodes'):
            return None
            
        lats = []
        lons = []
        
        for node_id, node_data in osm_data['nodes'].items():
            lats.append(node_data['lat'])
            lons.append(node_data['lon'])
        
        if not lats or not lons:
            return None
            
        self.bounds = (min(lons), min(lats), max(lons), max(lats))
        return self.bounds
    
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
        
        # Convert to pixel coordinates
        x = ((lon - (min_lon - (max_lon - min_lon) * padding)) / lon_range) * self.width
        y = ((max_lat + (max_lat - min_lat) * padding - lat) / lat_range) * self.height
        
        return (int(x), int(y))
    
    def draw_osm_data(self, osm_data):
        """Draw OSM data on canvas."""
        self.canvas.delete("all")
        
        # Calculate bounds
        if not self.calculate_bounds(osm_data):
            self.canvas.create_text(self.width//2, self.height//2, 
                                  text="No valid coordinate data found", 
                                  fill="red", font=("Arial", 14))
            return
        
        # Draw ways first (roads, buildings, etc.)
        if self.show_ways.get():
            self.draw_ways(osm_data.get('ways', {}))
        
        # Draw nodes if enabled
        if self.show_nodes.get():
            self.draw_nodes(osm_data.get('nodes', {}))
        
        # Add title
        self.canvas.create_text(10, 10, text="OSM Map Preview", 
                              anchor='nw', fill="black", font=("Arial", 12, "bold"))
        
        # Add bounds info
        if self.bounds:
            bounds_text = f"Bounds: {self.bounds[0]:.4f}, {self.bounds[1]:.4f} to {self.bounds[2]:.4f}, {self.bounds[3]:.4f}"
            self.canvas.create_text(10, self.height - 20, text=bounds_text, 
                                  anchor='sw', fill="gray", font=("Arial", 8))
    
    def draw_ways(self, ways):
        """Draw ways (roads, buildings, etc.) on canvas."""
        for way_id, way_data in ways.items():
            nodes = way_data.get('nodes', [])
            if len(nodes) < 2:
                continue
            
            # Determine way type and color
            tags = way_data.get('tags', {})
            way_type = self.get_way_type(tags)
            color = self.colors.get(way_type, self.colors['way'])
            
            # Draw way
            points = []
            for node_id in nodes:
                if node_id in self.nodes:
                    node_data = self.nodes[node_id]
                    pixel = self.latlon_to_pixel(node_data['lat'], node_data['lon'])
                    if pixel:
                        points.append(pixel)
            
            if len(points) >= 2:
                # Draw line or polygon
                if way_type == 'building' and len(points) >= 3:
                    # Draw as polygon
                    self.canvas.create_polygon(points, outline=color, fill=color, width=2)
                else:
                    # Draw as line
                    self.canvas.create_line(points, fill=color, width=2)
    
    def draw_nodes(self, nodes):
        """Draw nodes on canvas."""
        for node_id, node_data in nodes.items():
            pixel = self.latlon_to_pixel(node_data['lat'], node_data['lon'])
            if pixel:
                x, y = pixel
                self.canvas.create_oval(x-2, y-2, x+2, y+2, 
                                      fill=self.colors['node'], outline=self.colors['node'])
    
    def get_way_type(self, tags):
        """Determine way type from tags."""
        if 'building' in tags:
            return 'building'
        elif 'highway' in tags:
            return 'road'
        elif 'waterway' in tags:
            return 'water'
        else:
            return 'way'
    
    def update_display_settings(self, show_nodes, show_ways, show_buildings, show_roads):
        """Update display settings."""
        self.show_nodes.set(show_nodes)
        self.show_ways.set(show_ways)
        self.show_buildings.set(show_buildings)
        self.show_roads.set(show_roads)

class MapOSMGUI:
    """GUI with map visualization for OSM processing."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OSM Map Processor - with Map Visualization")
        self.root.geometry("1200x800")
        
        self.osm_file_path = None
        self.osm_data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Create main paned window
        paned = ttk.PanedWindow(self.root, orient='horizontal')
        paned.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Left panel - Controls
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # Right panel - Map
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        self.setup_control_panel(left_frame)
        self.setup_map_panel(right_frame)
        
    def setup_control_panel(self, parent):
        """Setup control panel."""
        # File selection
        file_group = ttk.LabelFrame(parent, text="File Selection", padding="10")
        file_group.pack(fill='x', padx=5, pady=5)
        
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_group, textvariable=self.file_path_var, state='readonly')
        file_entry.pack(fill='x', pady=(0, 5))
        
        ttk.Button(file_group, text="Browse OSM File", command=self.browse_file).pack(fill='x')
        
        # Load button
        ttk.Button(file_group, text="Load OSM File", command=self.load_osm_file, 
                  style='Accent.TButton').pack(fill='x', pady=(5, 0))
        
        # Status
        self.status_var = tk.StringVar(value="No file loaded")
        status_label = ttk.Label(file_group, textvariable=self.status_var)
        status_label.pack(pady=(5, 0))
        
        # Display controls
        display_group = ttk.LabelFrame(parent, text="Display Controls", padding="10")
        display_group.pack(fill='x', padx=5, pady=5)
        
        self.show_nodes_var = tk.BooleanVar(value=False)
        self.show_ways_var = tk.BooleanVar(value=True)
        self.show_buildings_var = tk.BooleanVar(value=True)
        self.show_roads_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(display_group, text="Show Nodes", variable=self.show_nodes_var,
                       command=self.refresh_map).pack(anchor='w')
        ttk.Checkbutton(display_group, text="Show Ways", variable=self.show_ways_var,
                       command=self.refresh_map).pack(anchor='w')
        ttk.Checkbutton(display_group, text="Show Buildings", variable=self.show_buildings_var,
                       command=self.refresh_map).pack(anchor='w')
        ttk.Checkbutton(display_group, text="Show Roads", variable=self.show_roads_var,
                       command=self.refresh_map).pack(anchor='w')
        
        # Color controls
        color_group = ttk.LabelFrame(parent, text="Colors", padding="10")
        color_group.pack(fill='x', padx=5, pady=5)
        
        color_frame = ttk.Frame(color_group)
        color_frame.pack(fill='x')
        
        colors = ['background', 'road', 'building', 'water', 'node']
        self.color_vars = {}
        
        for i, color_name in enumerate(colors):
            ttk.Label(color_frame, text=color_name.title()).grid(row=i, column=0, sticky='w')
            var = tk.StringVar(value=self.map_canvas.colors.get(color_name, '#000000'))
            self.color_vars[color_name] = var
            ttk.Entry(color_frame, textvariable=var, width=8).grid(row=i, column=1, padx=5)
            ttk.Button(color_frame, text="...", width=3, 
                      command=lambda c=color_name: self.choose_color(c)).grid(row=i, column=2)
        
        # Statistics
        stats_group = ttk.LabelFrame(parent, text="Statistics", padding="10")
        stats_group.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.stats_text = scrolledtext.ScrolledText(stats_group, height=10)
        self.stats_text.pack(fill='both', expand=True)
        
    def setup_map_panel(self, parent):
        """Setup map panel."""
        map_group = ttk.LabelFrame(parent, text="Map Preview", padding="10")
        map_group.pack(fill='both', expand=True)
        
        # Create map canvas
        self.map_canvas = SimpleMapCanvas(map_group, width=800, height=600)
        
        # Map controls
        map_controls = ttk.Frame(map_group)
        map_controls.pack(fill='x', pady=(5, 0))
        
        ttk.Button(map_controls, text="Refresh Map", command=self.refresh_map).pack(side='left')
        ttk.Button(map_controls, text="Clear Map", command=self.clear_map).pack(side='left', padx=(5, 0))
        ttk.Button(map_controls, text="Export Map", command=self.export_map).pack(side='right')
        
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
        """Load and parse OSM file."""
        if not self.osm_file_path:
            messagebox.showerror("Error", "Please select an OSM file first")
            return
        
        def load_in_thread():
            try:
                self.status_var.set("Loading OSM file...")
                self.root.update()
                
                # Parse OSM file
                self.osm_data = self.parse_osm_file(self.osm_file_path)
                
                # Update statistics
                self.update_statistics()
                
                # Draw map
                self.refresh_map()
                
                self.status_var.set(f"File loaded: {len(self.osm_data.get('nodes', {}))} nodes, {len(self.osm_data.get('ways', {}))} ways")
                
            except Exception as e:
                self.status_var.set("Error loading file")
                messagebox.showerror("Error", f"Failed to load OSM file: {e}")
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=load_in_thread)
        thread.daemon = True
        thread.start()
    
    def parse_osm_file(self, osm_file_path):
        """Parse OSM file and extract nodes and ways."""
        tree = ET.parse(osm_file_path)
        root = tree.getroot()
        
        osm_data = {
            'nodes': {},
            'ways': {},
            'relations': {}
        }
        
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
            
            osm_data['nodes'][node_id] = {
                'lat': lat,
                'lon': lon,
                'tags': tags
            }
        
        # Parse ways
        for way in root.findall('way'):
            way_id = int(way.get('id'))
            
            # Get nodes
            nodes = []
            for nd in way.findall('nd'):
                node_id = int(nd.get('ref'))
                if node_id in osm_data['nodes']:
                    nodes.append(node_id)
            
            # Get tags
            tags = {}
            for tag in way.findall('tag'):
                key = tag.get('k')
                value = tag.get('v')
                if key and value:
                    tags[key] = value
            
            if nodes:  # Only add ways with valid nodes
                osm_data['ways'][way_id] = {
                    'nodes': nodes,
                    'tags': tags
                }
        
        # Store nodes in map canvas for coordinate lookup
        self.map_canvas.nodes = osm_data['nodes']
        self.map_canvas.ways = osm_data['ways']
        
        return osm_data
    
    def update_statistics(self):
        """Update statistics display."""
        if not self.osm_data:
            return
        
        stats_text = f"""
OSM File Statistics
{'='*40}

📊 Basic Counts:
• Nodes: {len(self.osm_data.get('nodes', {})):,}
• Ways: {len(self.osm_data.get('ways', {})):,}
• Relations: {len(self.osm_data.get('relations', {})):,}

🏗️ Way Types:
"""
        
        # Count way types
        way_types = {}
        for way_data in self.osm_data.get('ways', {}).values():
            tags = way_data.get('tags', {})
            way_type = self.map_canvas.get_way_type(tags)
            way_types[way_type] = way_types.get(way_type, 0) + 1
        
        for way_type, count in way_types.items():
            stats_text += f"• {way_type.title()}: {count:,}\n"
        
        stats_text += f"""
🗺️ Map Bounds:
"""
        
        if self.map_canvas.bounds:
            min_lon, min_lat, max_lon, max_lat = self.map_canvas.bounds
            stats_text += f"• Min: {min_lon:.4f}, {min_lat:.4f}\n"
            stats_text += f"• Max: {max_lon:.4f}, {max_lat:.4f}\n"
            stats_text += f"• Size: {max_lon - min_lon:.4f}° × {max_lat - min_lat:.4f}°\n"
        
        stats_text += f"""
📁 File Info:
• Path: {self.osm_file_path}
• Size: {Path(self.osm_file_path).stat().st_size / 1024 / 1024:.2f} MB
"""
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_text)
    
    def refresh_map(self):
        """Refresh map display."""
        if self.osm_data:
            self.map_canvas.draw_osm_data(self.osm_data)
    
    def clear_map(self):
        """Clear map display."""
        self.map_canvas.canvas.delete("all")
        self.map_canvas.canvas.create_text(
            self.map_canvas.width//2, self.map_canvas.height//2,
            text="No map data loaded", fill="gray", font=("Arial", 14)
        )
    
    def choose_color(self, color_name):
        """Choose color for map element."""
        current_color = self.color_vars[color_name].get()
        # Simple color input - in real implementation you'd use colorchooser
        color = tk.simpledialog.askstring("Color", f"Enter color for {color_name}:", 
                                        initialvalue=current_color)
        if color:
            self.color_vars[color_name].set(color)
            self.map_canvas.colors[color_name] = color
            self.refresh_map()
    
    def export_map(self):
        """Export map as image."""
        if not self.osm_data:
            messagebox.showwarning("Warning", "No map data to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Map",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                # Get PostScript data from canvas
                ps_data = self.map_canvas.canvas.postscript()
                
                # Save as PostScript (simple approach)
                with open(filename.replace('.png', '.ps'), 'w') as f:
                    f.write(ps_data)
                
                messagebox.showinfo("Success", f"Map exported to {filename.replace('.png', '.ps')}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export map: {e}")
    
    def run(self):
        """Run the GUI application."""
        self.root.mainloop()

def main():
    """Main function."""
    # Import tkinter.simpledialog for color input
    import tkinter.simpledialog
    tk.simpledialog = tkinter.simpledialog
    
    app = MapOSMGUI()
    app.run()

if __name__ == "__main__":
    main()
