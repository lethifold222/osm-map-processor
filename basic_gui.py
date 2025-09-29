#!/usr/bin/env python3
"""
Basic GUI for OSM file processing - minimal version.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
import json
from pathlib import Path
import threading

class BasicOSMGUI:
    """Basic OSM GUI."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OSM Processor - Basic Version")
        self.root.geometry("800x600")
        
        self.osm_file_path = None
        self.osm_data = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="🗺️ OSM Map Processor", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        file_frame.pack(fill='x', pady=(0, 10))
        
        # File path display
        self.file_path_var = tk.StringVar()
        file_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, 
                              state='readonly', width=50)
        file_entry.pack(pady=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="📁 Browse OSM File", 
                  command=self.browse_file).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="📊 Load & Analyze", 
                  command=self.load_file, style='Accent.TButton').pack(side='left')
        
        # Status
        self.status_var = tk.StringVar(value="Ready - Select an OSM file")
        status_label = ttk.Label(file_frame, textvariable=self.status_var, 
                               foreground="blue")
        status_label.pack(pady=(10, 0))
        
        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Analysis Results", padding="10")
        results_frame.pack(fill='both', expand=True)
        
        # Results text
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20, wrap=tk.WORD)
        self.results_text.pack(fill='both', expand=True)
        
        # Initial message
        initial_message = """
Welcome to OSM Map Processor! 🗺️

This program can:
• Load and analyze OSM (.osm) files
• Extract geographic data (nodes, ways, relations)
• Show statistics and information about the map data
• Export analysis results

Instructions:
1. Click "Browse OSM File" to select an .osm file
2. Click "Load & Analyze" to process the file
3. View the results in this window

Ready to start!
"""
        self.results_text.insert(tk.END, initial_message)
        
    def browse_file(self):
        """Browse for OSM file."""
        filename = filedialog.askopenfilename(
            title="Select OSM File",
            filetypes=[("OSM files", "*.osm"), ("XML files", "*.xml"), ("All files", "*.*")]
        )
        if filename:
            self.file_path_var.set(filename)
            self.osm_file_path = filename
            self.status_var.set(f"Selected: {Path(filename).name}")
    
    def load_file(self):
        """Load and analyze OSM file."""
        if not self.osm_file_path:
            messagebox.showerror("Error", "Please select an OSM file first")
            return
        
        def load_thread():
            try:
                self.status_var.set("Loading OSM file...")
                self.root.update()
                
                # Parse OSM file
                self.osm_data = self.parse_osm_file(self.osm_file_path)
                
                # Generate report
                report = self.generate_report()
                
                # Display results
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, report)
                
                self.status_var.set("Analysis completed successfully!")
                
            except Exception as e:
                self.status_var.set("Error loading file")
                error_msg = f"Failed to load OSM file: {str(e)}\n\nPlease check that the file is a valid OSM XML file."
                messagebox.showerror("Error", error_msg)
                
                # Show error in results
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, f"❌ Error: {error_msg}")
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=load_thread)
        thread.daemon = True
        thread.start()
    
    def parse_osm_file(self, file_path):
        """Parse OSM file."""
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        data = {
            'nodes': {},
            'ways': {},
            'relations': {},
            'bounds': None
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
        node_count = 0
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
            node_count += 1
        
        # Parse ways
        way_count = 0
        for way in root.findall('way'):
            way_id = int(way.get('id'))
            
            # Get nodes
            nodes = []
            for nd in way.findall('nd'):
                node_id = int(nd.get('ref'))
                if node_id in data['nodes']:
                    nodes.append(node_id)
            
            # Get tags
            tags = {}
            for tag in way.findall('tag'):
                key = tag.get('k')
                value = tag.get('v')
                if key and value:
                    tags[key] = value
            
            if nodes:  # Only add ways with valid nodes
                data['ways'][way_id] = {
                    'nodes': nodes,
                    'tags': tags
                }
                way_count += 1
        
        # Parse relations
        relation_count = 0
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
            relation_count += 1
        
        return data
    
    def generate_report(self):
        """Generate analysis report."""
        if not self.osm_data:
            return "No data available"
        
        report = []
        report.append("🗺️ OSM FILE ANALYSIS REPORT")
        report.append("=" * 50)
        report.append("")
        
        # Basic statistics
        nodes = len(self.osm_data['nodes'])
        ways = len(self.osm_data['ways'])
        relations = len(self.osm_data['relations'])
        
        report.append("📊 BASIC STATISTICS:")
        report.append(f"• Total Nodes: {nodes:,}")
        report.append(f"• Total Ways: {ways:,}")
        report.append(f"• Total Relations: {relations:,}")
        report.append(f"• Total Elements: {nodes + ways + relations:,}")
        report.append("")
        
        # Bounds information
        if self.osm_data['bounds']:
            bounds = self.osm_data['bounds']
            report.append("🗺️ MAP BOUNDS:")
            report.append(f"• Southwest: {bounds['minlat']:.6f}, {bounds['minlon']:.6f}")
            report.append(f"• Northeast: {bounds['maxlat']:.6f}, {bounds['maxlon']:.6f}")
            report.append(f"• Size: {bounds['maxlat'] - bounds['minlat']:.6f}° × {bounds['maxlon'] - bounds['minlon']:.6f}°")
            
            # Estimate area (rough calculation)
            lat_diff = bounds['maxlat'] - bounds['minlat']
            lon_diff = bounds['maxlon'] - bounds['minlon']
            avg_lat = (bounds['maxlat'] + bounds['minlat']) / 2
            # Rough conversion to square kilometers
            lat_km = lat_diff * 111.32
            lon_km = lon_diff * 111.32 * abs(avg_lat / 180 * 3.14159)
            area_km2 = lat_km * lon_km
            report.append(f"• Estimated Area: {area_km2:.2f} km²")
            report.append("")
        
        # Way type analysis
        way_types = {}
        buildings = 0
        roads = 0
        water_features = 0
        amenities = 0
        natural_features = 0
        other = 0
        
        for way_data in self.osm_data['ways'].values():
            tags = way_data['tags']
            
            if 'building' in tags:
                buildings += 1
            elif 'highway' in tags:
                roads += 1
                highway_type = tags['highway']
                way_types[highway_type] = way_types.get(highway_type, 0) + 1
            elif 'waterway' in tags or 'natural' in tags and tags['natural'] == 'water':
                water_features += 1
            elif 'amenity' in tags:
                amenities += 1
            elif 'natural' in tags:
                natural_features += 1
            else:
                other += 1
        
        report.append("🏗️ WAY TYPE ANALYSIS:")
        report.append(f"• Buildings: {buildings:,}")
        report.append(f"• Roads: {roads:,}")
        report.append(f"• Water Features: {water_features:,}")
        report.append(f"• Amenities: {amenities:,}")
        report.append(f"• Natural Features: {natural_features:,}")
        report.append(f"• Other: {other:,}")
        report.append("")
        
        # Road types
        if way_types:
            report.append("🛣️ ROAD TYPES:")
            for road_type, count in sorted(way_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                report.append(f"• {road_type.replace('_', ' ').title()}: {count:,}")
            if len(way_types) > 10:
                report.append(f"• ... and {len(way_types) - 10} more types")
            report.append("")
        
        # File information
        file_size = Path(self.osm_file_path).stat().st_size
        report.append("📁 FILE INFORMATION:")
        report.append(f"• File Path: {self.osm_file_path}")
        report.append(f"• File Size: {file_size / 1024 / 1024:.2f} MB")
        report.append(f"• Elements per MB: {(nodes + ways + relations) / (file_size / 1024 / 1024):.0f}")
        report.append("")
        
        # Data quality assessment
        report.append("🔍 DATA QUALITY ASSESSMENT:")
        if nodes > 0 and ways > 0:
            node_way_ratio = nodes / ways
            report.append(f"• Node/Way Ratio: {node_way_ratio:.2f}")
            if node_way_ratio > 10:
                report.append("  → High node density (detailed street network)")
            elif node_way_ratio > 5:
                report.append("  → Medium node density (moderate detail)")
            else:
                report.append("  → Low node density (simplified network)")
        
        if ways > 0 and relations > 0:
            way_relation_ratio = ways / relations
            report.append(f"• Way/Relation Ratio: {way_relation_ratio:.1f}")
            if way_relation_ratio < 100:
                report.append("  → High relation usage (complex data structures)")
            else:
                report.append("  → Low relation usage (simple data structures)")
        
        # Recommendations
        report.append("")
        report.append("💡 RECOMMENDATIONS:")
        total_elements = nodes + ways + relations
        if total_elements > 1000000:
            report.append("• Large dataset - consider using spatial filtering")
        elif total_elements > 100000:
            report.append("• Medium dataset - suitable for most applications")
        else:
            report.append("• Small dataset - good for detailed analysis")
        
        if buildings > ways * 0.3:
            report.append("• High building density - urban area")
        elif buildings > ways * 0.1:
            report.append("• Moderate building density - suburban area")
        else:
            report.append("• Low building density - rural area")
        
        report.append("")
        report.append("✅ Analysis completed successfully!")
        
        return "\n".join(report)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()

def main():
    """Main function."""
    app = BasicOSMGUI()
    app.run()

if __name__ == "__main__":
    main()
