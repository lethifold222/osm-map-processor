#!/usr/bin/env python3
"""
Screenshot export functionality for OSM Map Processor.
Creates actual screenshots of the Leaflet map with legend and statistics.
"""

import os
import tempfile
import base64
from datetime import datetime
import io
import json
import subprocess
import time

class MapScreenshotExporter:
    """Export map as actual screenshot using browser automation."""
    
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
    
    def create_screenshot_html(self, analysis_data, bounds=None, filters=None, title="OSM Քարտեզի Վերլուծություն"):
        """Create HTML page specifically designed for screenshot capture."""
        
        # Calculate filtered statistics
        stats = self._calculate_filtered_stats(analysis_data, filters)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        total_elements = sum(stats.values())
        
        # Create map URL with filters
        map_params = []
        if filters:
            for key, value in filters.items():
                if value:
                    map_params.append(f"{key}=true")
                else:
                    map_params.append(f"{key}=false")
        
        map_url = f"/map?{'&'.join(map_params)}" if map_params else "/map"
        
        html_content = f"""
<!DOCTYPE html>
<html lang="hy">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" />
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            background: white;
            overflow: hidden;
        }}
        
        .screenshot-container {{
            width: 1200px;
            height: 800px;
            margin: 0 auto;
            background: white;
            position: relative;
            border: 2px solid #dee2e6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            text-align: center;
            height: 80px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .header h1 {{
            margin: 0;
            font-size: 1.8em;
            font-weight: bold;
        }}
        
        .header p {{
            margin: 5px 0 0 0;
            font-size: 1em;
            opacity: 0.9;
        }}
        
        .content {{
            display: flex;
            height: calc(100% - 80px);
        }}
        
        .map-section {{
            flex: 2;
            position: relative;
        }}
        
        .sidebar {{
            flex: 1;
            background: #f8f9fa;
            padding: 20px;
            border-left: 1px solid #dee2e6;
            overflow-y: auto;
        }}
        
        #map {{
            width: 100%;
            height: 100%;
            z-index: 1;
        }}
        
        .legend {{
            margin-bottom: 20px;
        }}
        
        .legend h5 {{
            color: #495057;
            margin-bottom: 15px;
            font-size: 1.1em;
            border-bottom: 2px solid #007bff;
            padding-bottom: 8px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            margin-bottom: 8px;
            padding: 5px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
            border: 2px solid white;
            box-shadow: 0 1px 2px rgba(0,0,0,0.2);
        }}
        
        .legend-label {{
            font-weight: bold;
            color: #495057;
            font-size: 0.9em;
        }}
        
        .stats-section {{
            margin-bottom: 20px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }}
        
        .stat-card {{
            background: white;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .stat-number {{
            font-size: 1.4em;
            font-weight: bold;
            margin-bottom: 3px;
        }}
        
        .stat-label {{
            color: #6c757d;
            font-size: 0.8em;
        }}
        
        .summary-stats {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 20px;
        }}
        
        .summary-stats h6 {{
            margin: 0 0 8px 0;
            font-size: 1em;
        }}
        
        .summary-number {{
            font-size: 2em;
            font-weight: bold;
            margin: 0;
        }}
        
        .timestamp {{
            color: #adb5bd;
            font-size: 0.7em;
            text-align: center;
            margin-top: 10px;
        }}
        
        .loading-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }}
        
        .loading-spinner {{
            width: 50px;
            height: 50px;
            border: 5px solid #f3f3f3;
            border-top: 5px solid #007bff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <div class="screenshot-container">
        <div class="header">
            <h1>🗺️ {title}</h1>
            <p>OpenStreetMap տվյալների մանրամասն վերլուծություն</p>
        </div>
        
        <div class="content">
            <div class="map-section">
                <div id="map"></div>
                <div class="loading-overlay" id="loadingOverlay">
                    <div class="loading-spinner"></div>
                </div>
            </div>
            
            <div class="sidebar">
                <div class="summary-stats">
                    <h6>Ընդհանուր Տարրեր</h6>
                    <p class="summary-number">{total_elements:,}</p>
                </div>
                
                <div class="legend">
                    <h5>🎨 Լեգենդ</h5>
        """
        
        # Add legend items based on filters
        for category, color in self.colors.items():
            if not filters or filters.get(category, True):
                label = self.armenian_labels[category]
                count = stats.get(category, 0)
                if count > 0:
                    html_content += f"""
                    <div class="legend-item">
                        <div class="legend-color" style="background-color: {color};"></div>
                        <div class="legend-label">{label} ({count:,})</div>
                    </div>
                    """
        
        html_content += f"""
                </div>
                
                <div class="stats-section">
                    <h5>📊 Վիճակագրություն</h5>
                    <div class="stats-grid">
        """
        
        # Add statistics cards
        for category, count in stats.items():
            if count > 0:
                color = self.colors[category]
                label = self.armenian_labels[category]
                html_content += f"""
                        <div class="stat-card">
                            <div class="stat-number" style="color: {color};">{count:,}</div>
                            <div class="stat-label">{label}</div>
                        </div>
                """
        
        html_content += f"""
                    </div>
                </div>
                
                <div class="timestamp">
                    Ստեղծված: {timestamp}
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>
    <script>
        // Initialize map
        let map = L.map('map', {{
            center: [40.1776, 44.5126],
            zoom: 13,
            zoomControl: false,
            attributionControl: false
        }});
        
        // Add tile layer
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);
        
        // Load map data
        async function loadMapData() {{
            try {{
                const params = new URLSearchParams();
        """
        
        # Add filter parameters to JavaScript
        if filters:
            for key, value in filters.items():
                html_content += f"                params.append('{key}', {str(value).lower()});\n"
        
        html_content += """
                const response = await fetch(`/api/map_data?${params.toString()}`);
                const data = await response.json();
                
                // Add markers and layers based on data
                addMapElements(data);
                
                // Hide loading overlay
                document.getElementById('loadingOverlay').style.display = 'none';
                
            } catch (error) {
                console.error('Error loading map data:', error);
                document.getElementById('loadingOverlay').style.display = 'none';
            }
        }
        
        function addMapElements(data) {
            // Add buildings
            if (data.ways) {
                Object.values(data.ways).forEach(way => {
                    const tags = way.tags;
                    if (tags.building) {
                        // Add building marker
                        if (way.coordinates && way.coordinates.length > 0) {
                            const lat = way.coordinates[0][1];
                            const lon = way.coordinates[0][0];
                            L.circleMarker([lat, lon], {
                                radius: 3,
                                fillColor: '#ff6b6b',
                                color: '#fff',
                                weight: 1,
                                opacity: 0.8,
                                fillOpacity: 0.8
                            }).addTo(map);
                        }
                    }
                });
            }
            
            // Add amenities
            if (data.nodes) {
                Object.values(data.nodes).forEach(node => {
                    const amenity = node.tags?.amenity;
                    const lat = node.lat;
                    const lon = node.lon;
                    
                    let color = '#007bff';
                    if (['school', 'university', 'college'].includes(amenity)) color = '#28a745';
                    else if (['hospital', 'clinic', 'pharmacy'].includes(amenity)) color = '#dc3545';
                    else if (['museum', 'theatre', 'cinema'].includes(amenity)) color = '#ffc107';
                    else if (['hotel', 'guest_house'].includes(amenity)) color = '#17a2b8';
                    else if (['restaurant', 'cafe', 'bar'].includes(amenity)) color = '#6c757d';
                    else if (['shop', 'supermarket'].includes(amenity)) color = '#343a40';
                    
                    L.circleMarker([lat, lon], {
                        radius: 4,
                        fillColor: color,
                        color: '#fff',
                        weight: 2,
                        opacity: 0.9,
                        fillOpacity: 0.9
                    }).addTo(map);
                });
            }
        }
        
        // Load data when page is ready
        document.addEventListener('DOMContentLoaded', function() {
            loadMapData();
        });
        
        // Signal when map is ready for screenshot
        setTimeout(() => {
            window.mapReady = true;
        }, 3000);
    </script>
</body>
</html>
        """
        
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
    
    def create_screenshot_export(self, analysis_data, bounds=None, filters=None, title="OSM Քարտեզի Վերլուծություն"):
        """Create screenshot export using browser automation."""
        
        # Generate HTML content
        html_content = self.create_screenshot_html(analysis_data, bounds, filters, title)
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_html_path = f.name
        
        try:
            # Use wkhtmltoimage for screenshot (if available)
            screenshot_path = temp_html_path.replace('.html', '.png')
            
            # Try to use wkhtmltoimage
            cmd = [
                'wkhtmltoimage',
                '--width', '1200',
                '--height', '800',
                '--quality', '95',
                '--format', 'png',
                temp_html_path,
                screenshot_path
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0 and os.path.exists(screenshot_path):
                    # Read the screenshot
                    with open(screenshot_path, 'rb') as f:
                        image_data = f.read()
                    
                    # Clean up
                    os.unlink(screenshot_path)
                    os.unlink(temp_html_path)
                    
                    return io.BytesIO(image_data)
                else:
                    raise Exception("wkhtmltoimage failed")
                    
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                # Fallback: return HTML content for manual screenshot
                html_buffer = io.BytesIO()
                html_buffer.write(html_content.encode('utf-8'))
                html_buffer.seek(0)
                
                # Clean up
                os.unlink(temp_html_path)
                
                return html_buffer
                
        except Exception as e:
            # Clean up on error
            try:
                os.unlink(temp_html_path)
            except:
                pass
            
            # Return HTML as fallback
            html_buffer = io.BytesIO()
            html_buffer.write(html_content.encode('utf-8'))
            html_buffer.seek(0)
            return html_buffer
