from __future__ import annotations
import tkinter as tk
from tkinter import ttk, colorchooser
from typing import Dict, Any, Optional, Callable, List
import geopandas as gpd
from .map_styles import MapStyleManager, get_highway_priority, get_waterway_priority
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import pandas as pd

class LayerController:
    """Interactive layer controller with real-time map preview."""
    
    def __init__(self, parent_frame: tk.Widget, layers_data: Dict[str, Any]):
        self.parent_frame = parent_frame
        self.layers_data = layers_data
        self.style_manager = MapStyleManager()
        
        # Layer visibility states
        self.layer_visibility = {
            'roads': True,
            'buildings': True,
            'waterways': True,
            'amenities': {},
            'pois': {},
            'landuse': {}
        }
        
        # Layer colors (customizable)
        self.layer_colors = {}
        
        # Callback for map updates
        self.map_update_callback: Optional[Callable] = None
        
        # Create UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the layer control interface."""
        # Main container
        self.main_frame = ttk.Frame(self.parent_frame)
        self.main_frame.pack(fill='both', expand=True)
        
        # Left panel - Layer controls
        self.left_panel = ttk.Frame(self.main_frame)
        self.left_panel.pack(side='left', fill='y', padx=(0, 5))
        self.left_panel.configure(width=300)
        
        # Right panel - Map preview
        self.right_panel = ttk.Frame(self.main_frame)
        self.right_panel.pack(side='right', fill='both', expand=True)
        
        self.setup_layer_controls()
        self.setup_map_preview()
        
    def setup_layer_controls(self):
        """Setup layer control widgets."""
        # Scrollable frame for layers
        canvas = tk.Canvas(self.left_panel)
        scrollbar = ttk.Scrollbar(self.left_panel, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main layers
        self.create_main_layer_section(scrollable_frame)
        
        # Roads sublayers
        if 'roads' in self.layers_data and self.layers_data['roads'] is not None:
            self.create_roads_section(scrollable_frame)
        
        # Buildings
        if 'buildings' in self.layers_data and self.layers_data['buildings'] is not None:
            self.create_buildings_section(scrollable_frame)
        
        # Waterways
        if 'waterways' in self.layers_data and self.layers_data['waterways'] is not None:
            self.create_waterways_section(scrollable_frame)
        
        # Amenities
        if 'amenities' in self.layers_data:
            self.create_amenities_section(scrollable_frame)
        
        # POIs
        if 'pois' in self.layers_data:
            self.create_pois_section(scrollable_frame)
        
        # Landuse
        if 'landuse' in self.layers_data:
            self.create_landuse_section(scrollable_frame)
        
        # Style controls
        self.create_style_controls(scrollable_frame)
        
    def create_main_layer_section(self, parent):
        """Create main layer visibility controls."""
        frame = ttk.LabelFrame(parent, text="Main Layers")
        frame.pack(fill='x', padx=5, pady=5)
        
        self.main_layer_vars = {}
        
        for layer in ['roads', 'buildings', 'waterways']:
            if layer in self.layers_data and self.layers_data[layer] is not None:
                var = tk.BooleanVar(value=True)
                self.main_layer_vars[layer] = var
                
                row_frame = ttk.Frame(frame)
                row_frame.pack(fill='x', padx=5, pady=2)
                
                ttk.Checkbutton(row_frame, text=layer.title(), variable=var,
                              command=lambda l=layer: self.on_layer_toggle(l)).pack(side='left')
                
                ttk.Button(row_frame, text="Color", width=6,
                          command=lambda l=layer: self.choose_layer_color(l)).pack(side='right')
    
    def create_roads_section(self, parent):
        """Create roads sublayer controls."""
        frame = ttk.LabelFrame(parent, text="Road Types")
        frame.pack(fill='x', padx=5, pady=5)
        
        roads_gdf = self.layers_data['roads']
        if 'highway' in roads_gdf.columns:
            highway_types = sorted(roads_gdf['highway'].unique(), key=get_highway_priority, reverse=True)
            
            self.road_vars = {}
            for highway_type in highway_types:
                if pd.isna(highway_type):
                    continue
                    
                var = tk.BooleanVar(value=True)
                self.road_vars[highway_type] = var
                
                row_frame = ttk.Frame(frame)
                row_frame.pack(fill='x', padx=5, pady=1)
                
                ttk.Checkbutton(row_frame, text=f"{highway_type}", variable=var,
                              command=lambda ht=highway_type: self.on_road_toggle(ht)).pack(side='left')
                
                ttk.Button(row_frame, text="●", width=3,
                          command=lambda ht=highway_type: self.choose_road_color(ht)).pack(side='right')
    
    def create_buildings_section(self, parent):
        """Create buildings controls."""
        frame = ttk.LabelFrame(parent, text="Buildings")
        frame.pack(fill='x', padx=5, pady=5)
        
        self.building_var = tk.BooleanVar(value=True)
        
        row_frame = ttk.Frame(frame)
        row_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Checkbutton(row_frame, text="Buildings", variable=self.building_var,
                      command=self.on_building_toggle).pack(side='left')
        
        ttk.Button(row_frame, text="Color", width=6,
                  command=self.choose_building_color).pack(side='right')
    
    def create_waterways_section(self, parent):
        """Create waterways controls."""
        frame = ttk.LabelFrame(parent, text="Waterways")
        frame.pack(fill='x', padx=5, pady=5)
        
        waterways_gdf = self.layers_data['waterways']
        if 'waterway' in waterways_gdf.columns:
            waterway_types = sorted(waterways_gdf['waterway'].unique(), key=get_waterway_priority, reverse=True)
            
            self.waterway_vars = {}
            for waterway_type in waterway_types:
                if pd.isna(waterway_type):
                    continue
                    
                var = tk.BooleanVar(value=True)
                self.waterway_vars[waterway_type] = var
                
                row_frame = ttk.Frame(frame)
                row_frame.pack(fill='x', padx=5, pady=1)
                
                ttk.Checkbutton(row_frame, text=f"{waterway_type}", variable=var,
                              command=lambda wt=waterway_type: self.on_waterway_toggle(wt)).pack(side='left')
                
                ttk.Button(row_frame, text="●", width=3,
                          command=lambda wt=waterway_type: self.choose_waterway_color(wt)).pack(side='right')
    
    def create_amenities_section(self, parent):
        """Create amenities controls."""
        frame = ttk.LabelFrame(parent, text="Amenities")
        frame.pack(fill='x', padx=5, pady=5)
        
        self.amenity_vars = {}
        
        for amenity_type, amenity_gdf in self.layers_data['amenities'].items():
            if amenity_gdf is not None and not amenity_gdf.empty:
                var = tk.BooleanVar(value=True)
                self.amenity_vars[amenity_type] = var
                
                row_frame = ttk.Frame(frame)
                row_frame.pack(fill='x', padx=5, pady=1)
                
                ttk.Checkbutton(row_frame, text=f"{amenity_type} ({len(amenity_gdf)})", 
                              variable=var, command=lambda at=amenity_type: self.on_amenity_toggle(at)).pack(side='left')
                
                ttk.Button(row_frame, text="●", width=3,
                          command=lambda at=amenity_type: self.choose_amenity_color(at)).pack(side='right')
    
    def create_pois_section(self, parent):
        """Create POIs controls."""
        frame = ttk.LabelFrame(parent, text="Points of Interest")
        frame.pack(fill='x', padx=5, pady=5)
        
        self.poi_vars = {}
        
        for poi_type, poi_gdf in self.layers_data['pois'].items():
            if poi_gdf is not None and not poi_gdf.empty:
                var = tk.BooleanVar(value=True)
                self.poi_vars[poi_type] = var
                
                row_frame = ttk.Frame(frame)
                row_frame.pack(fill='x', padx=5, pady=1)
                
                ttk.Checkbutton(row_frame, text=f"{poi_type} ({len(poi_gdf)})", 
                              variable=var, command=lambda pt=poi_type: self.on_poi_toggle(pt)).pack(side='left')
                
                ttk.Button(row_frame, text="●", width=3,
                          command=lambda pt=poi_type: self.choose_poi_color(pt)).pack(side='right')
    
    def create_landuse_section(self, parent):
        """Create landuse controls."""
        frame = ttk.LabelFrame(parent, text="Land Use")
        frame.pack(fill='x', padx=5, pady=5)
        
        self.landuse_vars = {}
        
        for landuse_type, landuse_gdf in self.layers_data['landuse'].items():
            if landuse_gdf is not None and not landuse_gdf.empty:
                var = tk.BooleanVar(value=True)
                self.landuse_vars[landuse_type] = var
                
                row_frame = ttk.Frame(frame)
                row_frame.pack(fill='x', padx=5, pady=1)
                
                ttk.Checkbutton(row_frame, text=f"{landuse_type} ({len(landuse_gdf)})", 
                              variable=var, command=lambda lt=landuse_type: self.on_landuse_toggle(lt)).pack(side='left')
                
                ttk.Button(row_frame, text="●", width=3,
                          command=lambda lt=landuse_type: self.choose_landuse_color(lt)).pack(side='right')
    
    def create_style_controls(self, parent):
        """Create style control widgets."""
        frame = ttk.LabelFrame(parent, text="Style Controls")
        frame.pack(fill='x', padx=5, pady=5)
        
        # Background color
        bg_frame = ttk.Frame(frame)
        bg_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(bg_frame, text="Background:").pack(side='left')
        self.bg_color_var = tk.StringVar(value="#f5f5f3")
        ttk.Entry(bg_frame, textvariable=self.bg_color_var, width=10).pack(side='left', padx=5)
        ttk.Button(bg_frame, text="Choose", command=self.choose_background_color).pack(side='right')
        
        # Map style
        style_frame = ttk.Frame(frame)
        style_frame.pack(fill='x', padx=5, pady=2)
        
        ttk.Label(style_frame, text="Style:").pack(side='left')
        self.style_var = tk.StringVar(value="osm")
        style_combo = ttk.Combobox(style_frame, textvariable=self.style_var, values=["osm", "minimal", "custom"])
        style_combo.pack(side='left', padx=5)
        style_combo.bind('<<ComboboxSelected>>', self.on_style_changed)
        
        # Update button
        ttk.Button(frame, text="Update Map", command=self.update_map).pack(fill='x', padx=5, pady=5)
    
    def setup_map_preview(self):
        """Setup map preview with matplotlib."""
        # Create matplotlib figure
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.right_panel)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, self.right_panel)
        toolbar.update()
        
        # Initial map render
        self.update_map()
    
    def on_layer_toggle(self, layer_name: str):
        """Handle main layer toggle."""
        self.layer_visibility[layer_name] = self.main_layer_vars[layer_name].get()
        self.update_map()
    
    def on_road_toggle(self, highway_type: str):
        """Handle road type toggle."""
        if highway_type not in self.layer_visibility['roads']:
            self.layer_visibility['roads'] = {}
        self.layer_visibility['roads'][highway_type] = self.road_vars[highway_type].get()
        self.update_map()
    
    def on_building_toggle(self):
        """Handle building toggle."""
        self.layer_visibility['buildings'] = self.building_var.get()
        self.update_map()
    
    def on_waterway_toggle(self, waterway_type: str):
        """Handle waterway type toggle."""
        if waterway_type not in self.layer_visibility['waterways']:
            self.layer_visibility['waterways'] = {}
        self.layer_visibility['waterways'][waterway_type] = self.waterway_vars[waterway_type].get()
        self.update_map()
    
    def on_amenity_toggle(self, amenity_type: str):
        """Handle amenity toggle."""
        self.layer_visibility['amenities'][amenity_type] = self.amenity_vars[amenity_type].get()
        self.update_map()
    
    def on_poi_toggle(self, poi_type: str):
        """Handle POI toggle."""
        self.layer_visibility['pois'][poi_type] = self.poi_vars[poi_type].get()
        self.update_map()
    
    def on_landuse_toggle(self, landuse_type: str):
        """Handle landuse toggle."""
        self.layer_visibility['landuse'][landuse_type] = self.landuse_vars[landuse_type].get()
        self.update_map()
    
    def on_style_changed(self, event):
        """Handle style change."""
        self.update_map()
    
    def choose_layer_color(self, layer_name: str):
        """Choose color for main layer."""
        current_color = self.layer_colors.get(layer_name, "#666666")
        color = colorchooser.askcolor(color=current_color)[1]
        if color:
            self.layer_colors[layer_name] = color
            self.update_map()
    
    def choose_road_color(self, highway_type: str):
        """Choose color for road type."""
        key = f"roads_{highway_type}"
        current_color = self.layer_colors.get(key, "#666666")
        color = colorchooser.askcolor(color=current_color)[1]
        if color:
            self.layer_colors[key] = color
            self.update_map()
    
    def choose_building_color(self):
        """Choose color for buildings."""
        current_color = self.layer_colors.get('buildings', "#cccccc")
        color = colorchooser.askcolor(color=current_color)[1]
        if color:
            self.layer_colors['buildings'] = color
            self.update_map()
    
    def choose_waterway_color(self, waterway_type: str):
        """Choose color for waterway type."""
        key = f"waterways_{waterway_type}"
        current_color = self.layer_colors.get(key, "#aad3df")
        color = colorchooser.askcolor(color=current_color)[1]
        if color:
            self.layer_colors[key] = color
            self.update_map()
    
    def choose_amenity_color(self, amenity_type: str):
        """Choose color for amenity type."""
        key = f"amenities_{amenity_type}"
        current_color = self.layer_colors.get(key, "#ff6b6b")
        color = colorchooser.askcolor(color=current_color)[1]
        if color:
            self.layer_colors[key] = color
            self.update_map()
    
    def choose_poi_color(self, poi_type: str):
        """Choose color for POI type."""
        key = f"pois_{poi_type}"
        current_color = self.layer_colors.get(key, "#666666")
        color = colorchooser.askcolor(color=current_color)[1]
        if color:
            self.layer_colors[key] = color
            self.update_map()
    
    def choose_landuse_color(self, landuse_type: str):
        """Choose color for landuse type."""
        key = f"landuse_{landuse_type}"
        current_color = self.layer_colors.get(key, "#f0f0f0")
        color = colorchooser.askcolor(color=current_color)[1]
        if color:
            self.layer_colors[key] = color
            self.update_map()
    
    def choose_background_color(self):
        """Choose background color."""
        current_color = self.bg_color_var.get()
        color = colorchooser.askcolor(color=current_color)[1]
        if color:
            self.bg_color_var.set(color)
            self.update_map()
    
    def update_map(self):
        """Update the map preview."""
        self.ax.clear()
        
        # Set background color
        bg_color = self.bg_color_var.get()
        self.ax.set_facecolor(bg_color)
        
        # Get style configuration
        style_name = self.style_var.get()
        style_config = self.style_manager.get_style(style_name)
        
        # Plot layers based on visibility
        self.plot_visible_layers()
        
        # Set map properties
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self.ax.set_title('Interactive Map Preview', fontsize=12, fontweight='bold')
        
        # Refresh canvas
        self.canvas.draw()
        
        # Call callback if set
        if self.map_update_callback:
            self.map_update_callback()
    
    def plot_visible_layers(self):
        """Plot only visible layers."""
        # Plot landuse first (background)
        if 'landuse' in self.layers_data and self.layer_visibility.get('landuse', True):
            self.plot_landuse_layers()
        
        # Plot waterways
        if 'waterways' in self.layers_data and self.layer_visibility.get('waterways', True):
            self.plot_waterway_layers()
        
        # Plot roads
        if 'roads' in self.layers_data and self.layer_visibility.get('roads', True):
            self.plot_road_layers()
        
        # Plot buildings
        if 'buildings' in self.layers_data and self.layer_visibility.get('buildings', True):
            self.plot_building_layers()
        
        # Plot amenities
        if 'amenities' in self.layers_data:
            self.plot_amenity_layers()
        
        # Plot POIs
        if 'pois' in self.layers_data:
            self.plot_poi_layers()
    
    def plot_landuse_layers(self):
        """Plot landuse layers."""
        for landuse_type, landuse_gdf in self.layers_data['landuse'].items():
            if (landuse_gdf is not None and not landuse_gdf.empty and 
                self.layer_visibility['landuse'].get(landuse_type, True)):
                
                color = self.layer_colors.get(f"landuse_{landuse_type}", "#f0f0f0")
                landuse_gdf.plot(ax=self.ax, color=color, edgecolor='#dddddd', 
                               linewidth=0.3, alpha=0.7)
    
    def plot_waterway_layers(self):
        """Plot waterway layers."""
        waterways_gdf = self.layers_data['waterways']
        if 'waterway' in waterways_gdf.columns:
            for waterway_type in waterways_gdf['waterway'].unique():
                if (pd.isna(waterway_type) or 
                    not self.layer_visibility['waterways'].get(waterway_type, True)):
                    continue
                
                waterway_subset = waterways_gdf[waterways_gdf['waterway'] == waterway_type]
                color = self.layer_colors.get(f"waterways_{waterway_type}", "#aad3df")
                
                waterway_subset.plot(ax=self.ax, color=color, linewidth=1.5, alpha=0.8)
    
    def plot_road_layers(self):
        """Plot road layers."""
        roads_gdf = self.layers_data['roads']
        if 'highway' in roads_gdf.columns:
            for highway_type in roads_gdf['highway'].unique():
                if (pd.isna(highway_type) or 
                    not self.layer_visibility['roads'].get(highway_type, True)):
                    continue
                
                road_subset = roads_gdf[roads_gdf['highway'] == highway_type]
                color = self.layer_colors.get(f"roads_{highway_type}", "#666666")
                
                road_subset.plot(ax=self.ax, color=color, linewidth=1.0, alpha=0.9)
    
    def plot_building_layers(self):
        """Plot building layers."""
        buildings_gdf = self.layers_data['buildings']
        color = self.layer_colors.get('buildings', "#cccccc")
        
        buildings_gdf.plot(ax=self.ax, color=color, edgecolor='#999999', 
                          linewidth=0.5, alpha=0.8)
    
    def plot_amenity_layers(self):
        """Plot amenity layers."""
        for amenity_type, amenity_gdf in self.layers_data['amenities'].items():
            if (amenity_gdf is not None and not amenity_gdf.empty and 
                self.layer_visibility['amenities'].get(amenity_type, True)):
                
                color = self.layer_colors.get(f"amenities_{amenity_type}", "#ff6b6b")
                
                # Convert to points if needed
                if amenity_gdf.geometry.geom_type.isin(['LineString', 'Polygon']).any():
                    points_gdf = amenity_gdf.copy()
                    points_gdf['geometry'] = points_gdf.geometry.centroid
                else:
                    points_gdf = amenity_gdf
                
                points_gdf.plot(ax=self.ax, color=color, marker='o', markersize=8, alpha=0.9)
    
    def plot_poi_layers(self):
        """Plot POI layers."""
        for poi_type, poi_gdf in self.layers_data['pois'].items():
            if (poi_gdf is not None and not poi_gdf.empty and 
                self.layer_visibility['pois'].get(poi_type, True)):
                
                color = self.layer_colors.get(f"pois_{poi_type}", "#666666")
                
                # Convert to points if needed
                if poi_gdf.geometry.geom_type.isin(['LineString', 'Polygon']).any():
                    points_gdf = poi_gdf.copy()
                    points_gdf['geometry'] = points_gdf.geometry.centroid
                else:
                    points_gdf = poi_gdf
                
                points_gdf.plot(ax=self.ax, color=color, marker='s', markersize=6, alpha=0.9)
    
    def set_map_update_callback(self, callback: Callable):
        """Set callback function for map updates."""
        self.map_update_callback = callback
    
    def get_visibility_state(self) -> Dict[str, Any]:
        """Get current visibility state."""
        return self.layer_visibility.copy()
    
    def get_color_state(self) -> Dict[str, str]:
        """Get current color state."""
        return self.layer_colors.copy()
    
    def set_visibility_state(self, state: Dict[str, Any]):
        """Set visibility state."""
        self.layer_visibility = state.copy()
        self.update_ui_from_state()
        self.update_map()
    
    def set_color_state(self, colors: Dict[str, str]):
        """Set color state."""
        self.layer_colors = colors.copy()
        self.update_map()
    
    def update_ui_from_state(self):
        """Update UI widgets from current state."""
        # Update main layers
        for layer, var in self.main_layer_vars.items():
            var.set(self.layer_visibility.get(layer, True))
        
        # Update road types
        if hasattr(self, 'road_vars'):
            for road_type, var in self.road_vars.items():
                road_visibility = self.layer_visibility.get('roads', {})
                var.set(road_visibility.get(road_type, True))
        
        # Update building
        if hasattr(self, 'building_var'):
            self.building_var.set(self.layer_visibility.get('buildings', True))
        
        # Update waterway types
        if hasattr(self, 'waterway_vars'):
            for waterway_type, var in self.waterway_vars.items():
                waterway_visibility = self.layer_visibility.get('waterways', {})
                var.set(waterway_visibility.get(waterway_type, True))
        
        # Update amenities
        if hasattr(self, 'amenity_vars'):
            for amenity_type, var in self.amenity_vars.items():
                var.set(self.layer_visibility['amenities'].get(amenity_type, True))
        
        # Update POIs
        if hasattr(self, 'poi_vars'):
            for poi_type, var in self.poi_vars.items():
                var.set(self.layer_visibility['pois'].get(poi_type, True))
        
        # Update landuse
        if hasattr(self, 'landuse_vars'):
            for landuse_type, var in self.landuse_vars.items():
                var.set(self.layer_visibility['landuse'].get(landuse_type, True))
