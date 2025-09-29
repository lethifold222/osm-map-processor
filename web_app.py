#!/usr/bin/env python3
"""
Web-based OSM Map Processor using Flask.
No architecture dependencies - works everywhere!
"""

from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import xml.etree.ElementTree as ET
import json
import os
import tempfile
import zipfile
from pathlib import Path
from werkzeug.utils import secure_filename
import threading
from datetime import datetime
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'osm_processor_secret_key_2024'

# Configuration
UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'osm', 'xml'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class OSMProcessor:
    """OSM file processor for web interface."""
    
    def __init__(self):
        self.current_data = None
        self.analysis_results = None
    
    def parse_osm_file(self, file_path):
        """Parse OSM file and return structured data."""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            data = {
                'nodes': {},
                'ways': {},
                'relations': {},
                'bounds': None,
                'metadata': {
                    'file_name': Path(file_path).name,
                    'file_size': Path(file_path).stat().st_size,
                    'processed_at': datetime.now().isoformat()
                }
            }
            
            # Get bounds if available
            bounds = root.find('bounds')
            if bounds is not None:
                data['bounds'] = {
                    'minlat': float(bounds.get('minlat')),
                    'minlon': float(bounds.get('minlon')),
                    'maxlat': float(bounds.get('maxlat')),
                    'maxlon': float(bounds.get('maxlon'))
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
                
                data['nodes'][node_id] = {
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
                    nodes.append(node_id)
                
                # Get tags
                tags = {}
                for tag in way.findall('tag'):
                    key = tag.get('k')
                    value = tag.get('v')
                    if key and value:
                        tags[key] = value
                
                data['ways'][way_id] = {
                    'nodes': nodes,
                    'tags': tags
                }
            
            # Parse relations
            for relation in root.findall('relation'):
                relation_id = int(relation.get('id'))
                
                # Get members
                members = []
                for member in relation.findall('member'):
                    members.append({
                        'type': member.get('type'),
                        'ref': int(member.get('ref')),
                        'role': member.get('role')
                    })
                
                # Get tags
                tags = {}
                for tag in relation.findall('tag'):
                    key = tag.get('k')
                    value = tag.get('v')
                    if key and value:
                        tags[key] = value
                
                data['relations'][relation_id] = {
                    'members': members,
                    'tags': tags
                }
            
            self.current_data = data
            return data
            
        except Exception as e:
            raise Exception(f"Error parsing OSM file: {str(e)}")
    
    def analyze_data(self, data):
        """Analyze OSM data and generate statistics."""
        if not data:
            return None
        
        analysis = {
            'basic_stats': {
                'nodes': len(data['nodes']),
                'ways': len(data['ways']),
                'relations': len(data['relations']),
                'total_elements': len(data['nodes']) + len(data['ways']) + len(data['relations'])
            },
            'way_analysis': {},
            'tag_analysis': {},
            'bounds_info': data.get('bounds'),
            'quality_metrics': {}
        }
        
        # Way type analysis
        way_types = {}
        amenity_details = {}
        
        for way_data in data['ways'].values():
            tags = way_data['tags']
            
            # Count by main tag types
            if 'building' in tags:
                way_types['buildings'] = way_types.get('buildings', 0) + 1
            if 'highway' in tags:
                way_types['roads'] = way_types.get('roads', 0) + 1
                highway_type = tags['highway']
                way_types[f'highway_{highway_type}'] = way_types.get(f'highway_{highway_type}', 0) + 1
            if 'waterway' in tags:
                way_types['waterways'] = way_types.get('waterways', 0) + 1
            if 'amenity' in tags:
                way_types['amenities'] = way_types.get('amenities', 0) + 1
                
                # Detailed amenity analysis for ways
                amenity = tags['amenity']
                if amenity in ['school', 'university', 'college', 'kindergarten']:
                    amenity_details['education'] = amenity_details.get('education', 0) + 1
                elif amenity in ['hospital', 'clinic', 'pharmacy', 'doctors']:
                    amenity_details['healthcare'] = amenity_details.get('healthcare', 0) + 1
                elif amenity in ['museum', 'theatre', 'cinema', 'library', 'arts_centre']:
                    amenity_details['culture'] = amenity_details.get('culture', 0) + 1
                elif amenity in ['hotel', 'guest_house', 'hostel', 'tourist_info']:
                    amenity_details['tourism'] = amenity_details.get('tourism', 0) + 1
                elif amenity in ['restaurant', 'cafe', 'bar', 'fast_food']:
                    amenity_details['food'] = amenity_details.get('food', 0) + 1
                elif amenity in ['shop', 'supermarket', 'marketplace']:
                    amenity_details['shopping'] = amenity_details.get('shopping', 0) + 1
            if 'natural' in tags:
                way_types['natural'] = way_types.get('natural', 0) + 1
            if 'landuse' in tags:
                way_types['landuse'] = way_types.get('landuse', 0) + 1
        
        analysis['way_analysis'] = way_types
        
        # Analyze nodes for amenities (point features)
        for node_data in data['nodes'].values():
            tags = node_data['tags']
            if 'amenity' in tags:
                way_types['amenities'] = way_types.get('amenities', 0) + 1
                
                # Detailed amenity analysis for nodes
                amenity = tags['amenity']
                if amenity in ['school', 'university', 'college', 'kindergarten']:
                    amenity_details['education'] = amenity_details.get('education', 0) + 1
                elif amenity in ['hospital', 'clinic', 'pharmacy', 'doctors']:
                    amenity_details['healthcare'] = amenity_details.get('healthcare', 0) + 1
                elif amenity in ['museum', 'theatre', 'cinema', 'library', 'arts_centre']:
                    amenity_details['culture'] = amenity_details.get('culture', 0) + 1
                elif amenity in ['hotel', 'guest_house', 'hostel', 'tourist_info']:
                    amenity_details['tourism'] = amenity_details.get('tourism', 0) + 1
                elif amenity in ['restaurant', 'cafe', 'bar', 'fast_food']:
                    amenity_details['food'] = amenity_details.get('food', 0) + 1
                elif amenity in ['shop', 'supermarket', 'marketplace']:
                    amenity_details['shopping'] = amenity_details.get('shopping', 0) + 1
        
        # Add detailed amenity statistics
        analysis['amenity_details'] = amenity_details
        
        # Tag analysis
        all_tags = set()
        tag_counts = {}
        
        for element_type in ['nodes', 'ways', 'relations']:
            for element_data in data[element_type].values():
                for tag_key in element_data.get('tags', {}):
                    all_tags.add(tag_key)
                    tag_counts[tag_key] = tag_counts.get(tag_key, 0) + 1
        
        analysis['tag_analysis'] = {
            'unique_tags': len(all_tags),
            'most_common_tags': dict(sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20])
        }
        
        # Quality metrics
        if analysis['basic_stats']['nodes'] > 0 and analysis['basic_stats']['ways'] > 0:
            analysis['quality_metrics']['node_way_ratio'] = analysis['basic_stats']['nodes'] / analysis['basic_stats']['ways']
        
        if analysis['basic_stats']['ways'] > 0 and analysis['basic_stats']['relations'] > 0:
            analysis['quality_metrics']['way_relation_ratio'] = analysis['basic_stats']['ways'] / analysis['basic_stats']['relations']
        
        # Area calculation if bounds available
        if data.get('bounds'):
            bounds = data['bounds']
            lat_diff = bounds['maxlat'] - bounds['minlat']
            lon_diff = bounds['maxlon'] - bounds['minlon']
            avg_lat = (bounds['maxlat'] + bounds['minlat']) / 2
            
            # Rough conversion to square kilometers
            lat_km = lat_diff * 111.32
            lon_km = lon_diff * 111.32 * abs(avg_lat / 180 * 3.14159)
            area_km2 = lat_km * lon_km
            
            analysis['quality_metrics']['estimated_area_km2'] = area_km2
            analysis['quality_metrics']['elements_per_km2'] = analysis['basic_stats']['total_elements'] / area_km2 if area_km2 > 0 else 0
        
        self.analysis_results = analysis
        return analysis
    
    def export_results(self, format_type='json'):
        """Export analysis results in specified format."""
        if not self.analysis_results or not self.current_data:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == 'json':
            filename = f"osm_analysis_{timestamp}.json"
            filepath = os.path.join(RESULTS_FOLDER, filename)
            
            export_data = {
                'metadata': self.current_data['metadata'],
                'analysis': self.analysis_results,
                'raw_data_summary': {
                    'nodes_sample': dict(list(self.current_data['nodes'].items())[:5]),  # First 5 nodes
                    'ways_sample': dict(list(self.current_data['ways'].items())[:5]),    # First 5 ways
                    'relations_sample': dict(list(self.current_data['relations'].items())[:5])  # First 5 relations
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return filepath
        
        elif format_type == 'csv':
            filename = f"osm_statistics_{timestamp}.csv"
            filepath = os.path.join(RESULTS_FOLDER, filename)
            
            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Value'])
                
                # Basic stats
                for key, value in self.analysis_results['basic_stats'].items():
                    writer.writerow([key.replace('_', ' ').title(), value])
                
                # Way analysis
                for key, value in self.analysis_results['way_analysis'].items():
                    writer.writerow([f"Way Type: {key.replace('_', ' ').title()}", value])
                
                # Quality metrics
                for key, value in self.analysis_results['quality_metrics'].items():
                    writer.writerow([f"Quality: {key.replace('_', ' ').title()}", f"{value:.4f}" if isinstance(value, float) else value])
            
            return filepath
        
        return None

# Initialize processor
processor = OSMProcessor()

@app.context_processor
def inject_globals():
    """Inject global variables into all templates."""
    return {
        'analysis_results': processor.analysis_results,
        'current_data': processor.current_data
    }

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            # Process the file
            data = processor.parse_osm_file(filepath)
            analysis = processor.analyze_data(data)
            
            flash(f'File "{filename}" uploaded and analyzed successfully!')
            return redirect(url_for('results'))
            
        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            return redirect(url_for('index'))
    
    else:
        flash('Invalid file type. Please upload .osm or .xml files only.')
        return redirect(url_for('index'))

@app.route('/results')
def results():
    """Display analysis results."""
    if not processor.analysis_results:
        flash('No analysis results available. Please upload a file first.')
        return redirect(url_for('index'))
    
    return render_template('results.html', 
                         analysis=processor.analysis_results,
                         metadata=processor.current_data['metadata'])

@app.route('/api/data')
def api_data():
    """API endpoint for analysis data."""
    if not processor.analysis_results:
        return jsonify({'error': 'No data available'}), 404
    
    return jsonify({
        'analysis': processor.analysis_results,
        'metadata': processor.current_data['metadata']
    })

@app.route('/export/<format_type>')
def export_data(format_type):
    """Export data in specified format."""
    if format_type not in ['json', 'csv']:
        flash('Invalid export format')
        return redirect(url_for('results'))
    
    try:
        filepath = processor.export_results(format_type)
        if filepath:
            return send_file(filepath, as_attachment=True)
        else:
            flash('Export failed')
            return redirect(url_for('results'))
    except Exception as e:
        flash(f'Export error: {str(e)}')
        return redirect(url_for('results'))

@app.route('/map')
def map_view():
    """Simple map view."""
    if not processor.current_data:
        flash('No data available. Please upload a file first.')
        return redirect(url_for('index'))
    
    return render_template('map.html', 
                         bounds=processor.current_data.get('bounds'),
                         way_analysis=processor.analysis_results['way_analysis'],
                         all_data=processor.current_data)

@app.route('/api/map_data')
def api_map_data():
    """API endpoint for map data with filtering."""
    if not processor.current_data:
        return jsonify({'error': 'No data available'}), 404
    
    # Get filter parameters
    show_buildings = request.args.get('buildings', 'true').lower() == 'true'
    show_roads = request.args.get('roads', 'true').lower() == 'true'
    show_waterways = request.args.get('waterways', 'false').lower() == 'true'
    show_amenities = request.args.get('amenities', 'false').lower() == 'true'
    show_education = request.args.get('education', 'false').lower() == 'true'
    show_healthcare = request.args.get('healthcare', 'false').lower() == 'true'
    show_culture = request.args.get('culture', 'false').lower() == 'true'
    show_tourism = request.args.get('tourism', 'false').lower() == 'true'
    show_food = request.args.get('food', 'false').lower() == 'true'
    show_shopping = request.args.get('shopping', 'false').lower() == 'true'
    
    # Filter data based on selections
    filtered_data = {
        'bounds': processor.current_data.get('bounds'),
        'nodes': {},
        'ways': {}
    }
    
    # Filter ways
    for way_id, way_data in processor.current_data['ways'].items():
        tags = way_data['tags']
        include_way = False
        
        # Check if way matches any selected filters
        if show_buildings and 'building' in tags:
            include_way = True
        elif show_roads and 'highway' in tags:
            include_way = True
        elif show_waterways and 'waterway' in tags:
            include_way = True
        elif show_amenities and 'amenity' in tags:
            amenity_type = tags['amenity']
            if show_education and amenity_type in ['school', 'university', 'college', 'kindergarten']:
                include_way = True
            elif show_healthcare and amenity_type in ['hospital', 'clinic', 'pharmacy', 'doctors']:
                include_way = True
            elif show_culture and amenity_type in ['museum', 'theatre', 'cinema', 'library', 'arts_centre']:
                include_way = True
            elif show_tourism and amenity_type in ['hotel', 'guest_house', 'hostel', 'tourist_info']:
                include_way = True
            elif show_food and amenity_type in ['restaurant', 'cafe', 'bar', 'fast_food']:
                include_way = True
            elif show_shopping and amenity_type in ['shop', 'supermarket', 'marketplace']:
                include_way = True
        
        if include_way:
            filtered_data['ways'][way_id] = way_data
    
    # Filter nodes (for amenities that are points)
    for node_id, node_data in processor.current_data['nodes'].items():
        tags = node_data['tags']
        include_node = False
        
        if 'amenity' in tags:
            amenity_type = tags['amenity']
            if show_education and amenity_type in ['school', 'university', 'college', 'kindergarten']:
                include_node = True
            elif show_healthcare and amenity_type in ['hospital', 'clinic', 'pharmacy', 'doctors']:
                include_node = True
            elif show_culture and amenity_type in ['museum', 'theatre', 'cinema', 'library', 'arts_centre']:
                include_node = True
            elif show_tourism and amenity_type in ['hotel', 'guest_house', 'hostel', 'tourist_info']:
                include_node = True
            elif show_food and amenity_type in ['restaurant', 'cafe', 'bar', 'fast_food']:
                include_node = True
            elif show_shopping and amenity_type in ['shop', 'supermarket', 'marketplace']:
                include_node = True
        
        if include_node:
            filtered_data['nodes'][node_id] = node_data
    
    return jsonify(filtered_data)

@app.route('/export_map_pdf')
def export_map_pdf():
    """Export current map view as PDF."""
    if not processor.current_data:
        flash('No data available. Please upload a file first.')
        return redirect(url_for('index'))
    
    try:
        # Get current filter settings
        show_buildings = request.args.get('buildings', 'true').lower() == 'true'
        show_roads = request.args.get('roads', 'true').lower() == 'true'
        show_waterways = request.args.get('waterways', 'false').lower() == 'true'
        show_education = request.args.get('education', 'false').lower() == 'true'
        show_healthcare = request.args.get('healthcare', 'false').lower() == 'true'
        show_culture = request.args.get('culture', 'false').lower() == 'true'
        show_tourism = request.args.get('tourism', 'false').lower() == 'true'
        show_food = request.args.get('food', 'false').lower() == 'true'
        show_shopping = request.args.get('shopping', 'false').lower() == 'true'
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"osm_map_report_{timestamp}.txt"
        
        # Create simple PDF content
        pdf_content = generate_simple_pdf_content(
            processor.current_data,
            processor.analysis_results,
            {
                'buildings': show_buildings,
                'roads': show_roads,
                'waterways': show_waterways,
                'education': show_education,
                'healthcare': show_healthcare,
                'culture': show_culture,
                'tourism': show_tourism,
                'food': show_food,
                'shopping': show_shopping
            }
        )
        
        # Create PDF buffer
        pdf_buffer = BytesIO(pdf_content.encode('utf-8'))
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='text/plain'
        )
        
    except Exception as e:
        flash(f'PDF export failed: {str(e)}')
        return redirect(url_for('map_view'))

def generate_simple_pdf_content(data, analysis, filters):
    """Generate simple PDF content as plain text."""
    
    # Count filtered data
    stats = {
        'buildings': 0,
        'roads': 0,
        'waterways': 0,
        'education': 0,
        'healthcare': 0,
        'culture': 0,
        'tourism': 0,
        'food': 0,
        'shopping': 0
    }
    
    # Count ways
    for way_data in data['ways'].values():
        tags = way_data['tags']
        if filters['buildings'] and 'building' in tags:
            stats['buildings'] += 1
        elif filters['roads'] and 'highway' in tags:
            stats['roads'] += 1
        elif filters['waterways'] and 'waterway' in tags:
            stats['waterways'] += 1
    
    # Count amenities
    for node_data in data['nodes'].values():
        if 'amenity' in node_data['tags']:
            amenity = node_data['tags']['amenity']
            if filters['education'] and amenity in ['school', 'university', 'college', 'kindergarten']:
                stats['education'] += 1
            elif filters['healthcare'] and amenity in ['hospital', 'clinic', 'pharmacy', 'doctors']:
                stats['healthcare'] += 1
            elif filters['culture'] and amenity in ['museum', 'theatre', 'cinema', 'library', 'arts_centre']:
                stats['culture'] += 1
            elif filters['tourism'] and amenity in ['hotel', 'guest_house', 'hostel', 'tourist_info']:
                stats['tourism'] += 1
            elif filters['food'] and amenity in ['restaurant', 'cafe', 'bar', 'fast_food']:
                stats['food'] += 1
            elif filters['shopping'] and amenity in ['shop', 'supermarket', 'marketplace']:
                stats['shopping'] += 1
    
    # Generate active filters list
    active_filters = []
    for filter_name, is_active in filters.items():
        if is_active:
            active_filters.append(filter_name.replace('_', ' ').title())
    
    bounds = data.get('bounds')
    bounds_text = ""
    if bounds:
        bounds_text = f"""
    Southwest: {bounds['minlat']:.6f}, {bounds['minlon']:.6f}
    Northeast: {bounds['maxlat']:.6f}, {bounds['maxlon']:.6f}
    Size: {bounds['maxlat'] - bounds['minlat']:.6f}° × {bounds['maxlon'] - bounds['minlon']:.6f}°"""
    
    # Generate PDF content as plain text
    content = f"""
================================================================================
                            🗺️ OSM MAP EXPORT REPORT
================================================================================

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source File: {data['metadata']['file_name']}

================================================================================
📊 MAP STATISTICS
================================================================================

Infrastructure:
    Buildings: {stats['buildings']:,}
    Roads: {stats['roads']:,}
    Waterways: {stats['waterways']:,}

Amenities:
    Education: {stats['education']:,}
    Healthcare: {stats['healthcare']:,}
    Culture: {stats['culture']:,}
    Tourism: {stats['tourism']:,}
    Food & Drink: {stats['food']:,}
    Shopping: {stats['shopping']:,}

================================================================================
🔍 ACTIVE FILTERS
================================================================================

Displayed Layers: {', '.join(active_filters) if active_filters else 'None'}

================================================================================
📋 MAP INFORMATION
================================================================================

File Name: {data['metadata']['file_name']}
File Size: {data['metadata']['file_size'] / 1024 / 1024:.2f} MB
Total Elements: {len(data['nodes']) + len(data['ways']) + len(data['relations']):,}
Nodes: {len(data['nodes']):,}
Ways: {len(data['ways']):,}
Relations: {len(data['relations']):,}{bounds_text}

================================================================================
🎨 LEGEND
================================================================================

Color Scheme:
    Buildings    - Red (#ff6b6b)
    Roads        - Teal (#4ecdc4)
    Waterways    - Blue (#45b7d1)
    Education    - Green (#28a745)
    Healthcare   - Red (#dc3545)
    Culture      - Yellow (#ffc107)
    Tourism      - Info Blue (#17a2b8)
    Food & Drink - Gray (#6c757d)
    Shopping     - Dark (#343a40)

================================================================================
                            END OF REPORT
================================================================================

Generated by OSM Map Processor Web Application
This report contains a summary of the OSM data analysis with current filter settings.
"""
    
    return content

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
