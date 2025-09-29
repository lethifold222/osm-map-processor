#!/usr/bin/env python3
"""
Simple image export functionality for OSM Map Processor.
Creates HTML-based visualizations that can be converted to images.
"""

import os
import tempfile
import base64
from datetime import datetime
import io
import json

class SimpleMapImageExporter:
    """Export map as HTML-based visualization."""
    
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
    
    def create_html_export(self, analysis_data, bounds=None, filters=None, title="OSM Քարտեզի Վերլուծություն"):
        """Create HTML-based export with legend and statistics."""
        
        # Calculate filtered statistics
        stats = self._calculate_filtered_stats(analysis_data, filters)
        
        # Generate HTML content
        html_content = self._generate_html_content(analysis_data, stats, filters, title)
        
        return html_content
    
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
    
    def _generate_html_content(self, analysis_data, stats, filters, title):
        """Generate HTML content for export."""
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        total_elements = sum(stats.values())
        
        html = f"""
<!DOCTYPE html>
<html lang="hy">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .content {{
            display: flex;
            min-height: 600px;
        }}
        
        .main-section {{
            flex: 2;
            padding: 30px;
        }}
        
        .sidebar {{
            flex: 1;
            background: #f8f9fa;
            padding: 30px;
            border-left: 1px solid #dee2e6;
        }}
        
        .legend {{
            margin-bottom: 30px;
        }}
        
        .legend h3 {{
            color: #495057;
            margin-bottom: 20px;
            font-size: 1.3em;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            padding: 10px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .legend-color {{
            width: 30px;
            height: 30px;
            border-radius: 50%;
            margin-right: 15px;
            border: 2px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        
        .legend-label {{
            font-weight: bold;
            color: #495057;
        }}
        
        .stats-section {{
            margin-bottom: 30px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-number {{
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #6c757d;
            font-size: 0.9em;
        }}
        
        .map-visualization {{
            background: linear-gradient(45deg, #f8f9fa 25%, transparent 25%), 
                        linear-gradient(-45deg, #f8f9fa 25%, transparent 25%), 
                        linear-gradient(45deg, transparent 75%, #f8f9fa 75%), 
                        linear-gradient(-45deg, transparent 75%, #f8f9fa 75%);
            background-size: 20px 20px;
            background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
            height: 300px;
            border-radius: 10px;
            position: relative;
            overflow: hidden;
            margin-bottom: 30px;
        }}
        
        .map-title {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(255,255,255,0.9);
            padding: 10px 20px;
            border-radius: 20px;
            font-weight: bold;
            color: #495057;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .summary-stats {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }}
        
        .summary-stats h3 {{
            margin: 0 0 15px 0;
            font-size: 1.5em;
        }}
        
        .summary-number {{
            font-size: 3em;
            font-weight: bold;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .footer {{
            background: #495057;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 0.9em;
        }}
        
        .timestamp {{
            color: #adb5bd;
            font-size: 0.8em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🗺️ {title}</h1>
            <p>OpenStreetMap տվյալների մանրամասն վերլուծություն</p>
        </div>
        
        <div class="content">
            <div class="main-section">
                <div class="map-visualization">
                    <div class="map-title">OSM Քարտեզի Վիզուալացում</div>
                </div>
                
                <div class="summary-stats">
                    <h3>Ընդհանուր Տարրեր</h3>
                    <p class="summary-number">{total_elements:,}</p>
                    <p>ակտիվ ֆիլտրներով</p>
                </div>
                
                <div class="stats-section">
                    <h3>Քարտեզի Վիճակագրություն</h3>
                    <div class="stats-grid">
        """
        
        # Add statistics cards
        for category, count in stats.items():
            if count > 0:  # Only show categories with data
                color = self.colors[category]
                label = self.armenian_labels[category]
                html += f"""
                        <div class="stat-card">
                            <div class="stat-number" style="color: {color};">{count:,}</div>
                            <div class="stat-label">{label}</div>
                        </div>
                """
        
        html += """
                    </div>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="legend">
                    <h3>🎨 Լեգենդ</h3>
        """
        
        # Add legend items
        for category, color in self.colors.items():
            if not filters or filters.get(category, True):
                label = self.armenian_labels[category]
                html += f"""
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: {color};"></div>
                        <div class="legend-label">{label}</div>
                    </div>
                """
        
        html += f"""
                </div>
                
                <div class="stats-section">
                    <h3>📊 Մանրամասն Վիճակագրություն</h3>
                    <div class="stats-grid">
        """
        
        # Add detailed statistics
        for category, count in stats.items():
            color = self.colors[category]
            label = self.armenian_labels[category]
            percentage = (count / total_elements * 100) if total_elements > 0 else 0
            html += f"""
                        <div class="stat-card">
                            <div class="stat-number" style="color: {color};">{count:,}</div>
                            <div class="stat-label">{label}</div>
                            <div class="stat-label">{percentage:.1f}%</div>
                        </div>
            """
        
        html += f"""
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Ստեղծված OSM Քարտեզի Մշակիչ-ով</p>
            <p class="timestamp">Ժամանակ: {timestamp}</p>
        </div>
    </div>
</body>
</html>
        """
        
        return html
    
    def create_export_file(self, analysis_data, bounds=None, filters=None, title="OSM Քարտեզի Վերլուծություն"):
        """Create export file and return as bytes."""
        
        html_content = self.create_html_export(analysis_data, bounds, filters, title)
        
        # Convert to bytes
        output_buffer = io.BytesIO()
        output_buffer.write(html_content.encode('utf-8'))
        output_buffer.seek(0)
        
        return output_buffer
