#!/usr/bin/env python3
"""
High-resolution image export functionality for OSM Map Processor.
Creates beautiful maps with legends and infographics.
"""

import os
import tempfile
import base64
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Rectangle, Circle
import io
import json

class MapImageExporter:
    """Export map as high-resolution image with legend and infographics."""
    
    def __init__(self):
        self.colors = {
            'buildings': '#ff6b6b',
            'roads': '#4ecdc4',
            'waterways': '#45b7d1',
            'education': '#28a745',
            'healthcare': '#dc3545',
            'culture': '#ffc107',
            'tourism': '#17a2b8',
            'food': '#6c757d',
            'shopping': '#343a40'
        }
        
        self.armenian_labels = {
            'buildings': 'Շենքեր',
            'roads': 'Ճանապարհներ',
            'waterways': 'Ջրային Ճանապարհներ',
            'education': 'Կրթություն',
            'healthcare': 'Առողջապահություն',
            'culture': 'Մշակույթ',
            'tourism': 'Տուրիզմ',
            'food': 'Սնունդ և Խմիչք',
            'shopping': 'Գնումներ'
        }
    
    def create_high_res_export(self, analysis_data, bounds=None, filters=None, title="OSM Քարտեզի Վերլուծություն"):
        """Create high-resolution map export with legend and statistics."""
        
        # Create figure with high DPI
        fig = plt.figure(figsize=(16, 12), dpi=300)
        fig.patch.set_facecolor('white')
        
        # Create main layout
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # Main map area (larger)
        map_ax = fig.add_subplot(gs[0:2, 0:3])
        
        # Legend area
        legend_ax = fig.add_subplot(gs[0:2, 3])
        legend_ax.axis('off')
        
        # Statistics area
        stats_ax = fig.add_subplot(gs[2, :])
        stats_ax.axis('off')
        
        # Draw map area
        self._draw_map_area(map_ax, bounds)
        
        # Draw legend
        self._draw_legend(legend_ax, filters)
        
        # Draw statistics
        self._draw_statistics(stats_ax, analysis_data, filters)
        
        # Add title
        fig.suptitle(title, fontsize=24, fontweight='bold', y=0.95)
        
        # Save to high-resolution image
        output_buffer = io.BytesIO()
        fig.savefig(output_buffer, format='PNG', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        output_buffer.seek(0)
        
        plt.close(fig)
        
        return output_buffer
    
    def _draw_map_area(self, ax, bounds):
        """Draw the main map area."""
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_aspect('equal')
        
        # Add background
        ax.add_patch(Rectangle((0, 0), 100, 100, facecolor='#f8f9fa', edgecolor='#dee2e6', linewidth=2))
        
        # Add grid
        for i in range(0, 101, 10):
            ax.axhline(y=i, color='#e9ecef', linewidth=0.5, alpha=0.5)
            ax.axvline(x=i, color='#e9ecef', linewidth=0.5, alpha=0.5)
        
        # Add sample map elements (simulated)
        self._add_sample_elements(ax)
        
        # Add title
        ax.set_title('OSM Քարտեզ', fontsize=16, fontweight='bold', pad=20)
        
        # Remove axes
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    def _add_sample_elements(self, ax):
        """Add sample map elements to demonstrate the layout."""
        # Sample buildings (rectangles)
        buildings = [(20, 20), (40, 30), (60, 25), (30, 60), (70, 50)]
        for x, y in buildings:
            rect = Rectangle((x-2, y-2), 4, 4, facecolor=self.colors['buildings'], 
                           alpha=0.8, edgecolor='white', linewidth=1)
            ax.add_patch(rect)
        
        # Sample roads (lines)
        road_points = [(10, 10, 90, 10), (10, 30, 90, 30), (10, 50, 90, 50), (10, 70, 90, 70)]
        for x1, y1, x2, y2 in road_points:
            ax.plot([x1, x2], [y1, y2], color=self.colors['roads'], linewidth=3, alpha=0.8)
        
        # Sample waterways (curved lines)
        ax.plot([10, 30, 50, 70, 90], [80, 75, 85, 78, 82], 
               color=self.colors['waterways'], linewidth=4, alpha=0.8)
        
        # Sample amenities (circles)
        amenities = {
            'education': [(15, 40), (45, 65)],
            'healthcare': [(25, 45), (55, 35)],
            'culture': [(35, 55), (65, 45)],
            'tourism': [(75, 60), (85, 40)],
            'food': [(15, 70), (45, 80)],
            'shopping': [(25, 80), (65, 70)]
        }
        
        for category, points in amenities.items():
            for x, y in points:
                circle = Circle((x, y), 2, facecolor=self.colors[category], 
                              alpha=0.8, edgecolor='white', linewidth=1)
                ax.add_patch(circle)
    
    def _draw_legend(self, ax, filters=None):
        """Draw the legend with Armenian labels."""
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 20)
        
        # Legend title
        ax.text(5, 19, 'Լեգենդ', fontsize=14, fontweight='bold', ha='center')
        
        # Legend items
        y_pos = 17
        for category, color in self.colors.items():
            if filters and not filters.get(category, True):
                continue
                
            # Color box
            rect = Rectangle((0.5, y_pos-0.3), 1, 0.6, facecolor=color, 
                           edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
            
            # Label
            ax.text(2, y_pos, self.armenian_labels[category], fontsize=10, va='center')
            
            y_pos -= 1.5
        
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    def _draw_statistics(self, ax, analysis_data, filters=None):
        """Draw statistics infographics."""
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 10)
        
        # Title
        ax.text(50, 9, 'Քարտեզի Վիճակագրություն', fontsize=16, fontweight='bold', ha='center')
        
        # Calculate filtered statistics
        stats = self._calculate_filtered_stats(analysis_data, filters)
        
        # Create bar chart
        categories = list(stats.keys())
        values = list(stats.values())
        colors = [self.colors[cat] for cat in categories]
        
        # Bar chart
        x_positions = [i * 10 + 5 for i in range(len(categories))]
        bars = ax.bar(x_positions, values, width=8, color=colors, alpha=0.8, edgecolor='white', linewidth=1)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                   f'{value:,}', ha='center', va='bottom', fontsize=8, fontweight='bold')
        
        # Add category labels
        for i, (category, pos) in enumerate(zip(categories, x_positions)):
            ax.text(pos, -0.5, self.armenian_labels[category], ha='center', va='top', 
                   fontsize=8, rotation=45)
        
        # Add summary statistics
        total = sum(values)
        ax.text(95, 8, f'Ընդհանուր: {total:,}', fontsize=12, fontweight='bold', ha='right')
        ax.text(95, 7, f'Ֆիլտրներ: {len([f for f in (filters or {}).values() if f])}', 
               fontsize=10, ha='right')
        
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    def _calculate_filtered_stats(self, analysis_data, filters=None):
        """Calculate statistics based on current filters."""
        stats = {}
        
        # Basic infrastructure
        if not filters or filters.get('buildings', True):
            stats['buildings'] = analysis_data.get('way_analysis', {}).get('buildings', 0)
        
        if not filters or filters.get('roads', True):
            stats['roads'] = analysis_data.get('way_analysis', {}).get('roads', 0)
        
        if not filters or filters.get('waterways', True):
            stats['waterways'] = analysis_data.get('way_analysis', {}).get('waterways', 0)
        
        # Amenities
        amenity_details = analysis_data.get('amenity_details', {})
        
        if not filters or filters.get('education', True):
            stats['education'] = amenity_details.get('education', 0)
        
        if not filters or filters.get('healthcare', True):
            stats['healthcare'] = amenity_details.get('healthcare', 0)
        
        if not filters or filters.get('culture', True):
            stats['culture'] = amenity_details.get('culture', 0)
        
        if not filters or filters.get('tourism', True):
            stats['tourism'] = amenity_details.get('tourism', 0)
        
        if not filters or filters.get('food', True):
            stats['food'] = amenity_details.get('food', 0)
        
        if not filters or filters.get('shopping', True):
            stats['shopping'] = amenity_details.get('shopping', 0)
        
        return stats
    
    def create_screenshot_export(self, map_data, analysis_data, filters=None):
        """Create a screenshot-style export with map data visualization."""
        
        # Create figure with high DPI
        fig = plt.figure(figsize=(20, 14), dpi=300)
        fig.patch.set_facecolor('white')
        
        # Create layout
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # Main visualization
        main_ax = fig.add_subplot(gs[:, :2])
        
        # Legend
        legend_ax = fig.add_subplot(gs[0, 2])
        legend_ax.axis('off')
        
        # Statistics
        stats_ax = fig.add_subplot(gs[1, 2])
        stats_ax.axis('off')
        
        # Draw main visualization
        self._draw_data_visualization(main_ax, map_data, analysis_data)
        
        # Draw legend
        self._draw_legend(legend_ax, filters)
        
        # Draw statistics
        self._draw_statistics(stats_ax, analysis_data, filters)
        
        # Add title and metadata
        title = f"OSM Քարտեզի Վերլուծություն - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        fig.suptitle(title, fontsize=20, fontweight='bold', y=0.95)
        
        # Add footer
        fig.text(0.5, 0.02, 'Ստեղծված OSM Քարտեզի Մշակիչ-ով', ha='center', fontsize=10, style='italic')
        
        # Save to high-resolution image
        output_buffer = io.BytesIO()
        fig.savefig(output_buffer, format='PNG', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        output_buffer.seek(0)
        
        plt.close(fig)
        
        return output_buffer
    
    def _draw_data_visualization(self, ax, map_data, analysis_data):
        """Draw the main data visualization."""
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.set_aspect('equal')
        
        # Background
        ax.add_patch(Rectangle((0, 0), 100, 100, facecolor='#f8f9fa', edgecolor='#dee2e6', linewidth=2))
        
        # Draw bounds if available
        if map_data.get('bounds'):
            bounds = map_data['bounds']
            # Convert to relative coordinates for visualization
            x1, y1 = 10, 10
            x2, y2 = 90, 90
            
            # Bounds rectangle
            bounds_rect = Rectangle((x1, y1), x2-x1, y2-y1, 
                                  facecolor='none', edgecolor='#007bff', linewidth=2, linestyle='--')
            ax.add_patch(bounds_rect)
            
            # Bounds info
            ax.text(x2, y2+2, f'Սահմաններ: {bounds["minlat"]:.4f}, {bounds["minlon"]:.4f}', 
                   fontsize=8, ha='right')
        
        # Visualize data distribution
        self._visualize_data_distribution(ax, analysis_data)
        
        # Title
        ax.set_title('OSM Տվյալների Վիզուալացում', fontsize=16, fontweight='bold', pad=20)
        
        # Remove axes
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    
    def _visualize_data_distribution(self, ax, analysis_data):
        """Visualize the distribution of different data types."""
        
        # Create a grid-based visualization
        grid_size = 10
        cell_size = 8
        
        # Calculate proportions
        way_analysis = analysis_data.get('way_analysis', {})
        total_elements = sum(way_analysis.values())
        
        if total_elements == 0:
            return
        
        # Distribute elements across grid
        categories = ['buildings', 'roads', 'waterways']
        colors = [self.colors[cat] for cat in categories]
        
        for i, (category, color) in enumerate(zip(categories, colors)):
            count = way_analysis.get(category, 0)
            if count == 0:
                continue
                
            # Calculate number of cells to fill
            proportion = count / total_elements
            cells_to_fill = max(1, int(proportion * grid_size * grid_size))
            
            # Fill cells
            for j in range(cells_to_fill):
                row = (j * 3 + i) // grid_size
                col = (j * 3 + i) % grid_size
                
                if row < grid_size and col < grid_size:
                    x = 10 + col * cell_size
                    y = 10 + row * cell_size
                    
                    rect = Rectangle((x, y), cell_size-1, cell_size-1, 
                                   facecolor=color, alpha=0.7, edgecolor='white', linewidth=0.5)
                    ax.add_patch(rect)
