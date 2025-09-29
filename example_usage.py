#!/usr/bin/env python3
"""
Example usage of the OSM Map Processor.
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

from config import AppConfig
from osm_pipeline import run_pipeline

def create_example_config():
    """Create an example configuration for testing."""
    config_data = {
        'project_name': 'example_osm_project',
        'input': {
            'osm_file': None,  # Will be set by user
            'bbox': [44.430, 40.090, 44.550, 40.230],  # Yerevan area
            'place': None
        },
        'output': {
            'output_dir': './example_outputs',
            'vector_formats': ['svg', 'pdf'],
            'geodata_formats': ['geojson'],
            'image_formats': ['png'],
            'enable_reports': True
        },
        'layers': {
            'roads': True,
            'buildings': True,
            'waterways': True,
            'amenities': ['school', 'hospital', 'restaurant'],
            'pois': ['bank', 'atm'],
            'landuse': ['residential', 'commercial', 'park']
        },
        'crs': {
            'target_epsg': 3857
        },
        'visualize': {
            'map_style': 'osm',
            'background_color': '#f5f5f3',
            'custom_colors': {}
        },
        'cache': {
            'enable_cache': True,
            'cache_dir': '.cache',
            'cache_ttl_hours': 24
        }
    }
    
    return AppConfig(**config_data)

def main():
    """Main example function."""
    print("OSM Map Processor - Example Usage")
    print("=" * 40)
    
    # Create example configuration
    config = create_example_config()
    
    print(f"Project: {config.project_name}")
    print(f"Input: {'OSM file' if config.input.osm_file else 'Bbox/Place'}")
    print(f"Output directory: {config.output.output_dir}")
    print(f"Layers: {[k for k, v in config.layers.model_dump().items() if isinstance(v, bool) and v]}")
    
    print("\nTo run with actual data:")
    print("1. Download an OSM file from https://www.openstreetmap.org/")
    print("2. Set the path in config.input.osm_file")
    print("3. Run: python example_usage.py")
    
    print("\nOr launch the GUI:")
    print("python -m app gui")

if __name__ == "__main__":
    main()
