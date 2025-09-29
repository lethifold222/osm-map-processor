from __future__ import annotations
from typing import Dict, Any, Optional, List, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

class MapStyleManager:
    """Manager for different map styles and color schemes."""
    
    def __init__(self):
        self.styles = {
            'osm': self._get_osm_style(),
            'minimal': self._get_minimal_style(),
            'custom': {}
        }
    
    def _get_osm_style(self) -> Dict[str, Any]:
        """OpenStreetMap-inspired style."""
        return {
            'background': '#f5f5f3',
            'water': '#aad3df',
            'landuse': {
                'residential': '#f2efe9',
                'commercial': '#f2e9e1', 
                'industrial': '#e8e8e8',
                'park': '#d8e8c8',
                'forest': '#c8e6c8',
                'grass': '#d8e8c8',
                'farmland': '#f2e9e1',
                'cemetery': '#e8e8e8'
            },
            'roads': {
                'motorway': {'color': '#ff9999', 'width': 3.0},
                'trunk': {'color': '#ff9999', 'width': 2.5},
                'primary': {'color': '#ffcc99', 'width': 2.0},
                'secondary': {'color': '#ffff99', 'width': 1.5},
                'tertiary': {'color': '#ffffff', 'width': 1.2},
                'residential': {'color': '#ffffff', 'width': 0.8},
                'service': {'color': '#ffffff', 'width': 0.5},
                'footway': {'color': '#cccccc', 'width': 0.3},
                'cycleway': {'color': '#99ccff', 'width': 0.8}
            },
            'buildings': {
                'color': '#f2efe9',
                'edgecolor': '#ddccaa',
                'linewidth': 0.5
            },
            'waterways': {
                'river': {'color': '#aad3df', 'width': 2.0},
                'stream': {'color': '#aad3df', 'width': 1.0},
                'canal': {'color': '#aad3df', 'width': 1.5},
                'ditch': {'color': '#aad3df', 'width': 0.8}
            },
            'pois': {
                'school': {'color': '#ff6b6b', 'marker': 's', 'size': 20},
                'hospital': {'color': '#4ecdc4', 'marker': 'H', 'size': 20},
                'restaurant': {'color': '#ffe66d', 'marker': 'o', 'size': 15},
                'bank': {'color': '#95e1d3', 'marker': 'D', 'size': 15},
                'atm': {'color': '#a8e6cf', 'marker': '^', 'size': 12},
                'pharmacy': {'color': '#ffb3ba', 'marker': 'p', 'size': 15},
                'fuel': {'color': '#ff9999', 'marker': 'o', 'size': 12},
                'parking': {'color': '#cccccc', 'marker': 'P', 'size': 10}
            }
        }
    
    def _get_minimal_style(self) -> Dict[str, Any]:
        """Minimal clean style."""
        return {
            'background': '#ffffff',
            'water': '#e6f3ff',
            'landuse': {
                'residential': '#f8f8f8',
                'commercial': '#f0f0f0',
                'industrial': '#e8e8e8',
                'park': '#f0f8f0',
                'forest': '#e8f5e8',
                'grass': '#f0f8f0'
            },
            'roads': {
                'motorway': {'color': '#666666', 'width': 2.5},
                'trunk': {'color': '#666666', 'width': 2.0},
                'primary': {'color': '#888888', 'width': 1.5},
                'secondary': {'color': '#aaaaaa', 'width': 1.2},
                'tertiary': {'color': '#cccccc', 'width': 1.0},
                'residential': {'color': '#dddddd', 'width': 0.8},
                'service': {'color': '#eeeeee', 'width': 0.5}
            },
            'buildings': {
                'color': '#f5f5f5',
                'edgecolor': '#dddddd',
                'linewidth': 0.3
            },
            'waterways': {
                'river': {'color': '#e6f3ff', 'width': 1.5},
                'stream': {'color': '#e6f3ff', 'width': 0.8},
                'canal': {'color': '#e6f3ff', 'width': 1.2}
            },
            'pois': {
                'school': {'color': '#ff6b6b', 'marker': 's', 'size': 15},
                'hospital': {'color': '#4ecdc4', 'marker': 'H', 'size': 15},
                'restaurant': {'color': '#ffe66d', 'marker': 'o', 'size': 12},
                'bank': {'color': '#95e1d3', 'marker': 'D', 'size': 12}
            }
        }
    
    def get_style(self, style_name: str) -> Dict[str, Any]:
        """Get style configuration by name."""
        return self.styles.get(style_name, self.styles['osm'])
    
    def get_layer_color(self, layer_name: str, sublayer_name: str = '', 
                       highway_type: str = '', waterway_type: str = '',
                       style_name: str = 'osm', custom_colors: Dict[str, str] = None) -> Dict[str, Any]:
        """Get color configuration for a specific layer."""
        style = self.get_style(style_name)
        custom_colors = custom_colors or {}
        
        # Check for custom color first
        custom_key = f"{layer_name}_{sublayer_name}" if sublayer_name else layer_name
        if custom_key in custom_colors:
            return {'color': custom_colors[custom_key]}
        
        # Get from style configuration
        if layer_name == 'roads' and highway_type:
            road_style = style.get('roads', {}).get(highway_type)
            if road_style:
                return road_style
        
        elif layer_name == 'waterways' and waterway_type:
            waterway_style = style.get('waterways', {}).get(waterway_type)
            if waterway_style:
                return waterway_style
        
        elif layer_name == 'buildings':
            return style.get('buildings', {'color': '#cccccc'})
        
        elif layer_name == 'landuse' and sublayer_name:
            landuse_colors = style.get('landuse', {})
            color = landuse_colors.get(sublayer_name, '#f0f0f0')
            return {'color': color, 'edgecolor': '#dddddd', 'linewidth': 0.3}
        
        elif layer_name in ['amenities', 'pois'] and sublayer_name:
            poi_style = style.get('pois', {}).get(sublayer_name)
            if poi_style:
                return poi_style
        
        # Default fallback
        return {'color': '#666666', 'linewidth': 0.5}

def apply_osm_style_to_axes(ax, style_config: Dict[str, Any]):
    """Apply OSM-style background and grid to matplotlib axes."""
    ax.set_facecolor(style_config.get('background', '#f5f5f3'))
    
    # Add subtle grid (OSM style)
    ax.grid(True, alpha=0.1, linewidth=0.5, color='#999999')
    
    # Set axis appearance
    ax.tick_params(colors='#666666', labelsize=8)
    for spine in ax.spines.values():
        spine.set_color('#cccccc')
        spine.set_linewidth(0.5)

def create_legend_for_osm_style(ax, layers: Dict[str, Any], style_config: Dict[str, Any]):
    """Create OSM-style legend."""
    legend_elements = []
    
    # Roads legend
    if 'roads' in layers and layers['roads'] is not None:
        roads_style = style_config.get('roads', {})
        for road_type, road_config in roads_style.items():
            legend_elements.append(
                plt.Line2D([0], [0], color=road_config['color'], 
                          linewidth=road_config['width'], 
                          label=f'{road_type.title()} Road')
            )
    
    # POIs legend
    pois_style = style_config.get('pois', {})
    for poi_type, poi_config in pois_style.items():
        legend_elements.append(
            plt.Line2D([0], [0], marker=poi_config['marker'], 
                      color='w', markerfacecolor=poi_config['color'],
                      markersize=8, label=f'{poi_type.title()}')
        )
    
    # Landuse legend
    landuse_style = style_config.get('landuse', {})
    for landuse_type, color in landuse_style.items():
        legend_elements.append(
            patches.Patch(color=color, label=f'{landuse_type.title()} Area')
        )
    
    if legend_elements:
        ax.legend(handles=legend_elements, loc='upper right', 
                 frameon=True, fancybox=True, shadow=True, 
                 fontsize=9, framealpha=0.9)

def get_highway_priority(highway_type: str) -> int:
    """Get drawing priority for highway types (higher = drawn later/on top)."""
    priority_map = {
        'motorway': 10, 'trunk': 9, 'primary': 8, 'secondary': 7,
        'tertiary': 6, 'residential': 5, 'service': 4, 'footway': 3,
        'cycleway': 2, 'path': 1
    }
    return priority_map.get(highway_type, 0)

def get_waterway_priority(waterway_type: str) -> int:
    """Get drawing priority for waterway types."""
    priority_map = {
        'river': 5, 'canal': 4, 'stream': 3, 'ditch': 2, 'drain': 1
    }
    return priority_map.get(waterway_type, 0)
