from __future__ import annotations
from typing import Optional, Dict, Any
from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import pandas as pd
from .map_styles import MapStyleManager, apply_osm_style_to_axes, create_legend_for_osm_style, get_highway_priority, get_waterway_priority

def preview_gdf(gdf: Optional[gpd.GeoDataFrame], title: str = "Preview", sample_n: int = 1000):
    if gdf is None or gdf.empty:
        return
    if len(gdf) > sample_n:
        gdf = gdf.sample(sample_n, random_state=42)
    ax = gdf.plot(figsize=(8, 8))
    ax.set_title(title)
    plt.tight_layout()
    plt.show()

def preview_layers(layers: Dict[str, gpd.GeoDataFrame], sample_n: int = 1000):
    for name, gdf in layers.items():
        preview_gdf(gdf, title=f"Layer: {name}", sample_n=sample_n)

def create_vector_map(layers: Dict[str, Any], output_path: Path, format: str = 'SVG') -> None:
    """Create a high-quality vector map from layers."""
    fig, ax = plt.subplots(figsize=(12, 10), dpi=300)
    
    # Define colors and styles for different layer types
    layer_styles = {
        'roads': {'color': '#666666', 'linewidth': 0.5, 'alpha': 0.8},
        'buildings': {'color': '#cccccc', 'linewidth': 0.3, 'alpha': 0.7},
        'school': {'color': '#ff6b6b', 'marker': 's', 'markersize': 20, 'alpha': 0.8},
        'hospital': {'color': '#4ecdc4', 'marker': 'H', 'markersize': 20, 'alpha': 0.8},
        'restaurant': {'color': '#ffe66d', 'marker': 'o', 'markersize': 15, 'alpha': 0.8},
        'bank': {'color': '#95e1d3', 'marker': 'D', 'markersize': 15, 'alpha': 0.8},
        'atm': {'color': '#a8e6cf', 'marker': '^', 'markersize': 12, 'alpha': 0.8},
        'pharmacy': {'color': '#ffb3ba', 'marker': 'p', 'markersize': 15, 'alpha': 0.8},
    }
    
    # Plot layers in order
    layer_order = ['roads', 'buildings'] + list(layers.keys())
    layer_order = [l for l in layer_order if l in layers and layers[l] is not None and not layers[l].empty]
    
    for layer_name in layer_order:
        gdf = layers[layer_name]
        if gdf is None or gdf.empty:
            continue
            
        style = layer_styles.get(layer_name, {'color': '#333333', 'linewidth': 0.5, 'alpha': 0.8})
        
        try:
            if layer_name == 'roads':
                # Roads as lines
                gdf.plot(ax=ax, color=style['color'], linewidth=style['linewidth'], 
                        alpha=style['alpha'], edgecolor='none')
            elif layer_name == 'buildings':
                # Buildings as polygons
                gdf.plot(ax=ax, color=style['color'], linewidth=style['linewidth'], 
                        alpha=style['alpha'], edgecolor='#999999')
            else:
                # POIs as points
                if 'geometry' in gdf.columns:
                    # Convert to points if needed
                    if gdf.geometry.geom_type.isin(['LineString', 'Polygon']).any():
                        # Get centroids for non-point geometries
                        points_gdf = gdf.copy()
                        points_gdf['geometry'] = points_gdf.geometry.centroid
                    else:
                        points_gdf = gdf
                    
                    points_gdf.plot(ax=ax, color=style['color'], marker=style.get('marker', 'o'),
                                  markersize=style.get('markersize', 10), alpha=style['alpha'])
        except Exception as e:
            print(f"Warning: Could not plot layer {layer_name}: {e}")
            continue
    
    # Styling
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('OSM Vector Map', fontsize=16, fontweight='bold', pad=20)
    
    # Add legend for POI layers
    legend_elements = []
    for layer_name in layer_order:
        if layer_name not in ['roads', 'buildings']:
            style = layer_styles.get(layer_name, {'color': '#333333', 'marker': 'o'})
            legend_elements.append(plt.Line2D([0], [0], marker=style.get('marker', 'o'), 
                                            color='w', markerfacecolor=style['color'],
                                            markersize=8, label=layer_name.title()))
    
    if legend_elements:
        ax.legend(handles=legend_elements, loc='upper right', frameon=True, 
                 fancybox=True, shadow=True, fontsize=10)
    
    plt.tight_layout()
    
    # Save in specified format
    if format.upper() == 'SVG':
        plt.savefig(output_path, format='svg', bbox_inches='tight', pad_inches=0.1)
    elif format.upper() == 'PDF':
        plt.savefig(output_path, format='pdf', bbox_inches='tight', pad_inches=0.1)
    elif format.upper() == 'EPS':
        plt.savefig(output_path, format='eps', bbox_inches='tight', pad_inches=0.1)
    
    plt.close(fig)

def create_raster_map(layers: Dict[str, Any], output_path: Path, format: str = 'PNG', dpi: int = 300) -> None:
    """Create a high-quality raster map from layers."""
    fig, ax = plt.subplots(figsize=(12, 10), dpi=dpi)
    
    # Define colors and styles for different layer types
    layer_styles = {
        'roads': {'color': '#666666', 'linewidth': 1.0, 'alpha': 0.9},
        'buildings': {'color': '#cccccc', 'linewidth': 0.5, 'alpha': 0.8},
        'school': {'color': '#ff6b6b', 'marker': 's', 'markersize': 30, 'alpha': 0.9},
        'hospital': {'color': '#4ecdc4', 'marker': 'H', 'markersize': 30, 'alpha': 0.9},
        'restaurant': {'color': '#ffe66d', 'marker': 'o', 'markersize': 25, 'alpha': 0.9},
        'bank': {'color': '#95e1d3', 'marker': 'D', 'markersize': 25, 'alpha': 0.9},
        'atm': {'color': '#a8e6cf', 'marker': '^', 'markersize': 20, 'alpha': 0.9},
        'pharmacy': {'color': '#ffb3ba', 'marker': 'p', 'markersize': 25, 'alpha': 0.9},
    }
    
    # Plot layers in order
    layer_order = ['roads', 'buildings'] + list(layers.keys())
    layer_order = [l for l in layer_order if l in layers and layers[l] is not None and not layers[l].empty]
    
    for layer_name in layer_order:
        gdf = layers[layer_name]
        if gdf is None or gdf.empty:
            continue
            
        style = layer_styles.get(layer_name, {'color': '#333333', 'linewidth': 1.0, 'alpha': 0.9})
        
        try:
            if layer_name == 'roads':
                # Roads as lines
                gdf.plot(ax=ax, color=style['color'], linewidth=style['linewidth'], 
                        alpha=style['alpha'], edgecolor='none')
            elif layer_name == 'buildings':
                # Buildings as polygons
                gdf.plot(ax=ax, color=style['color'], linewidth=style['linewidth'], 
                        alpha=style['alpha'], edgecolor='#999999')
            else:
                # POIs as points
                if 'geometry' in gdf.columns:
                    # Convert to points if needed
                    if gdf.geometry.geom_type.isin(['LineString', 'Polygon']).any():
                        # Get centroids for non-point geometries
                        points_gdf = gdf.copy()
                        points_gdf['geometry'] = points_gdf.geometry.centroid
                    else:
                        points_gdf = gdf
                    
                    points_gdf.plot(ax=ax, color=style['color'], marker=style.get('marker', 'o'),
                                  markersize=style.get('markersize', 15), alpha=style['alpha'])
        except Exception as e:
            print(f"Warning: Could not plot layer {layer_name}: {e}")
            continue
    
    # Styling
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('OSM Raster Map', fontsize=16, fontweight='bold', pad=20)
    
    # Add legend for POI layers
    legend_elements = []
    for layer_name in layer_order:
        if layer_name not in ['roads', 'buildings']:
            style = layer_styles.get(layer_name, {'color': '#333333', 'marker': 'o'})
            legend_elements.append(plt.Line2D([0], [0], marker=style.get('marker', 'o'), 
                                            color='w', markerfacecolor=style['color'],
                                            markersize=10, label=layer_name.title()))
    
    if legend_elements:
        ax.legend(handles=legend_elements, loc='upper right', frameon=True, 
                 fancybox=True, shadow=True, fontsize=10)
    
    plt.tight_layout()
    
    # Save in specified format
    if format.upper() == 'PNG':
        plt.savefig(output_path, format='png', bbox_inches='tight', pad_inches=0.1, dpi=dpi)
    elif format.upper() in ['JPG', 'JPEG']:
        plt.savefig(output_path, format='jpeg', bbox_inches='tight', pad_inches=0.1, dpi=dpi)
    
    plt.close(fig)
