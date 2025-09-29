from __future__ import annotations
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import xml.etree.ElementTree as ET
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon
from shapely.geometry import MultiPoint, MultiLineString, MultiPolygon
import logging

logger = logging.getLogger(__name__)

class OSMParser:
    """Parser for OSM XML files."""
    
    def __init__(self):
        self.nodes: Dict[int, Tuple[float, float]] = {}
        self.ways: Dict[int, Dict[str, Any]] = {}
        self.relations: Dict[int, Dict[str, Any]] = {}
        
    def parse_file(self, osm_file_path: str | Path) -> Dict[str, Any]:
        """Parse an OSM XML file and return structured data."""
        osm_file_path = Path(osm_file_path)
        
        if not osm_file_path.exists():
            raise FileNotFoundError(f"OSM file not found: {osm_file_path}")
            
        logger.info(f"Parsing OSM file: {osm_file_path}")
        
        # Parse XML
        tree = ET.parse(osm_file_path)
        root = tree.getroot()
        
        # Clear previous data
        self.nodes.clear()
        self.ways.clear()
        self.relations.clear()
        
        # Parse elements
        for element in root:
            if element.tag == 'node':
                self._parse_node(element)
            elif element.tag == 'way':
                self._parse_way(element)
            elif element.tag == 'relation':
                self._parse_relation(element)
        
        logger.info(f"Parsed {len(self.nodes)} nodes, {len(self.ways)} ways, {len(self.relations)} relations")
        
        # Convert to GeoDataFrames
        return self._to_geodataframes()
    
    def _parse_node(self, node_element: ET.Element) -> None:
        """Parse a node element."""
        node_id = int(node_element.get('id'))
        lat = float(node_element.get('lat'))
        lon = float(node_element.get('lon'))
        self.nodes[node_id] = (lon, lat)
    
    def _parse_way(self, way_element: ET.Element) -> None:
        """Parse a way element."""
        way_id = int(way_element.get('id'))
        way_data = {
            'id': way_id,
            'nodes': [],
            'tags': {}
        }
        
        for child in way_element:
            if child.tag == 'nd':
                way_data['nodes'].append(int(child.get('ref')))
            elif child.tag == 'tag':
                key = child.get('k')
                value = child.get('v')
                way_data['tags'][key] = value
        
        self.ways[way_id] = way_data
    
    def _parse_relation(self, relation_element: ET.Element) -> None:
        """Parse a relation element."""
        relation_id = int(relation_element.get('id'))
        relation_data = {
            'id': relation_id,
            'members': [],
            'tags': {}
        }
        
        for child in relation_element:
            if child.tag == 'member':
                member_data = {
                    'type': child.get('type'),
                    'ref': int(child.get('ref')),
                    'role': child.get('role', '')
                }
                relation_data['members'].append(member_data)
            elif child.tag == 'tag':
                key = child.get('k')
                value = child.get('v')
                relation_data['tags'][key] = value
        
        self.relations[relation_id] = relation_data
    
    def _to_geodataframes(self) -> Dict[str, Any]:
        """Convert parsed data to GeoDataFrames."""
        result = {}
        
        # Points (nodes with specific tags)
        points_data = []
        for node_id, (lon, lat) in self.nodes.items():
            # We'll collect nodes that are part of ways or have specific tags
            # For now, we'll skip individual nodes unless they have special meaning
            pass
        
        # Lines (ways)
        lines_data = []
        for way_id, way_data in self.ways.items():
            if len(way_data['nodes']) < 2:
                continue
                
            # Build geometry
            coordinates = []
            for node_id in way_data['nodes']:
                if node_id in self.nodes:
                    coordinates.append(self.nodes[node_id])
            
            if len(coordinates) < 2:
                continue
                
            geometry = LineString(coordinates)
            
            # Create feature data
            feature_data = {
                'id': way_id,
                'geometry': geometry,
                **way_data['tags']
            }
            lines_data.append(feature_data)
        
        if lines_data:
            result['ways'] = gpd.GeoDataFrame(lines_data, crs='EPSG:4326')
        
        # Polygons (closed ways)
        polygons_data = []
        for way_id, way_data in self.ways.items():
            if len(way_data['nodes']) < 3:
                continue
                
            # Check if way is closed
            if way_data['nodes'][0] != way_data['nodes'][-1]:
                continue
                
            # Build geometry
            coordinates = []
            for node_id in way_data['nodes']:
                if node_id in self.nodes:
                    coordinates.append(self.nodes[node_id])
            
            if len(coordinates) < 3:
                continue
                
            try:
                geometry = Polygon(coordinates)
                if not geometry.is_valid:
                    continue
                    
                # Create feature data
                feature_data = {
                    'id': way_id,
                    'geometry': geometry,
                    **way_data['tags']
                }
                polygons_data.append(feature_data)
            except Exception as e:
                logger.warning(f"Failed to create polygon for way {way_id}: {e}")
                continue
        
        if polygons_data:
            result['polygons'] = gpd.GeoDataFrame(polygons_data, crs='EPSG:4326')
        
        # Process relations for multipolygons
        multipolygons_data = []
        for rel_id, rel_data in self.relations.items():
            if rel_data['tags'].get('type') != 'multipolygon':
                continue
                
            # Simple multipolygon processing
            # This is a simplified version - full multipolygon support is complex
            outer_ways = []
            inner_ways = []
            
            for member in rel_data['members']:
                if member['type'] == 'way':
                    way_id = member['ref']
                    if way_id in self.ways:
                        if member['role'] == 'outer':
                            outer_ways.append(self.ways[way_id])
                        elif member['role'] == 'inner':
                            inner_ways.append(self.ways[way_id])
            
            if not outer_ways:
                continue
                
            # For simplicity, just use the first outer way
            outer_way = outer_ways[0]
            if len(outer_way['nodes']) < 3:
                continue
                
            coordinates = []
            for node_id in outer_way['nodes']:
                if node_id in self.nodes:
                    coordinates.append(self.nodes[node_id])
            
            if len(coordinates) < 3:
                continue
                
            try:
                geometry = Polygon(coordinates)
                if not geometry.is_valid:
                    continue
                    
                feature_data = {
                    'id': rel_id,
                    'geometry': geometry,
                    **rel_data['tags']
                }
                multipolygons_data.append(feature_data)
            except Exception as e:
                logger.warning(f"Failed to create multipolygon for relation {rel_id}: {e}")
                continue
        
        if multipolygons_data:
            result['multipolygons'] = gpd.GeoDataFrame(multipolygons_data, crs='EPSG:4326')
        
        return result


def load_osm_file(osm_file_path: str | Path) -> Dict[str, Any]:
    """Load and parse an OSM XML file.
    
    Returns a dictionary with GeoDataFrames for different geometry types.
    """
    parser = OSMParser()
    return parser.parse_file(osm_file_path)
