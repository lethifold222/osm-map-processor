from __future__ import annotations
from typing import Dict, Any, Optional
from pathlib import Path
import pandas as pd
import geopandas as gpd
from datetime import datetime

def generate_csv_summary(layers: Dict[str, Any], output_path: Path) -> None:
    """Generate CSV summary of layer statistics."""
    summary_data = []
    
    for layer_name, layer_data in layers.items():
        if layer_data is None:
            continue
            
        if isinstance(layer_data, dict):
            # Handle dictionary of layers (amenities, pois, landuse)
            for sublayer_name, sublayer_data in layer_data.items():
                if sublayer_data is not None and not sublayer_data.empty:
                    summary_data.append({
                        'layer': layer_name,
                        'sublayer': sublayer_name,
                        'count': len(sublayer_data),
                        'geometry_type': sublayer_data.geometry.geom_type.iloc[0] if len(sublayer_data) > 0 else 'unknown',
                        'crs': str(sublayer_data.crs) if sublayer_data.crs else 'unknown'
                    })
        else:
            # Handle single layers (roads, buildings, waterways)
            if hasattr(layer_data, 'empty') and not layer_data.empty:
                summary_data.append({
                    'layer': layer_name,
                    'sublayer': '',
                    'count': len(layer_data),
                    'geometry_type': layer_data.geometry.geom_type.iloc[0] if len(layer_data) > 0 else 'unknown',
                    'crs': str(layer_data.crs) if layer_data.crs else 'unknown'
                })
    
    if summary_data:
        df = pd.DataFrame(summary_data)
        df.to_csv(output_path, index=False)
        print(f"[i] Generated CSV summary: {output_path}")

def generate_markdown_report(layers: Dict[str, Any], config: Dict[str, Any], output_path: Path) -> None:
    """Generate Markdown report with layer statistics and project info."""
    
    report_lines = []
    report_lines.append("# OSM Data Processing Report")
    report_lines.append("")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    # Project info
    if 'project_name' in config:
        report_lines.append(f"**Project:** {config['project_name']}")
    report_lines.append("")
    
    # Input info
    report_lines.append("## Input Configuration")
    if 'input' in config:
        input_cfg = config['input']
        if 'bbox' in input_cfg and input_cfg['bbox']:
            bbox = input_cfg['bbox']
            report_lines.append(f"- **Bounding Box:** [{bbox[0]:.4f}, {bbox[1]:.4f}, {bbox[2]:.4f}, {bbox[3]:.4f}]")
        if 'place' in input_cfg and input_cfg['place']:
            report_lines.append(f"- **Place:** {input_cfg['place']}")
        if 'osm_file' in input_cfg and input_cfg['osm_file']:
            report_lines.append(f"- **OSM File:** {input_cfg['osm_file']}")
    report_lines.append("")
    
    # Layer statistics
    report_lines.append("## Layer Statistics")
    report_lines.append("")
    report_lines.append("| Layer | Sublayer | Count | Geometry Type | CRS |")
    report_lines.append("|-------|----------|-------|---------------|-----|")
    
    for layer_name, layer_data in layers.items():
        if layer_data is None:
            continue
            
        if isinstance(layer_data, dict):
            # Handle dictionary of layers
            for sublayer_name, sublayer_data in layer_data.items():
                if sublayer_data is not None and not sublayer_data.empty:
                    geom_type = sublayer_data.geometry.geom_type.iloc[0] if len(sublayer_data) > 0 else 'unknown'
                    crs = str(sublayer_data.crs) if sublayer_data.crs else 'unknown'
                    report_lines.append(f"| {layer_name} | {sublayer_name} | {len(sublayer_data)} | {geom_type} | {crs} |")
        else:
            # Handle single layers
            if hasattr(layer_data, 'empty') and not layer_data.empty:
                geom_type = layer_data.geometry.geom_type.iloc[0] if len(layer_data) > 0 else 'unknown'
                crs = str(layer_data.crs) if layer_data.crs else 'unknown'
                report_lines.append(f"| {layer_name} | - | {len(layer_data)} | {geom_type} | {crs} |")
    
    report_lines.append("")
    
    # Output info
    if 'output' in config:
        report_lines.append("## Output Configuration")
        output_cfg = config['output']
        if 'output_dir' in output_cfg:
            report_lines.append(f"- **Output Directory:** {output_cfg['output_dir']}")
        if 'geodata_formats' in output_cfg:
            report_lines.append(f"- **Geodata Formats:** {', '.join(output_cfg['geodata_formats'])}")
        if 'vector_formats' in output_cfg:
            report_lines.append(f"- **Vector Formats:** {', '.join(output_cfg['vector_formats'])}")
        if 'image_formats' in output_cfg:
            report_lines.append(f"- **Image Formats:** {', '.join(output_cfg['image_formats'])}")
    report_lines.append("")
    
    # Processing info
    report_lines.append("## Processing Information")
    report_lines.append("")
    if 'crs' in config and 'target_epsg' in config['crs']:
        report_lines.append(f"- **Target CRS:** EPSG:{config['crs']['target_epsg']}")
    if 'cache' in config:
        cache_cfg = config['cache']
        if 'enable_cache' in cache_cfg:
            report_lines.append(f"- **Caching:** {'Enabled' if cache_cfg['enable_cache'] else 'Disabled'}")
        if 'cache_ttl_hours' in cache_cfg:
            report_lines.append(f"- **Cache TTL:** {cache_cfg['cache_ttl_hours']} hours")
    report_lines.append("")
    
    # Layer details
    report_lines.append("## Layer Details")
    report_lines.append("")
    
    for layer_name, layer_data in layers.items():
        if layer_data is None:
            continue
            
        report_lines.append(f"### {layer_name.title()}")
        report_lines.append("")
        
        if isinstance(layer_data, dict):
            # Dictionary of layers
            for sublayer_name, sublayer_data in layer_data.items():
                if sublayer_data is not None and not sublayer_data.empty:
                    report_lines.append(f"#### {sublayer_name}")
                    report_lines.append(f"- **Count:** {len(sublayer_data)}")
                    if len(sublayer_data) > 0:
                        geom_type = sublayer_data.geometry.geom_type.iloc[0]
                        report_lines.append(f"- **Primary Geometry:** {geom_type}")
                        
                        # Show sample attributes
                        if hasattr(sublayer_data, 'columns'):
                            attr_cols = [c for c in sublayer_data.columns if c not in ['geometry']]
                            if attr_cols:
                                report_lines.append(f"- **Attributes:** {', '.join(attr_cols[:5])}")
                                if len(attr_cols) > 5:
                                    report_lines.append(f"  - *... and {len(attr_cols) - 5} more*")
                    report_lines.append("")
        else:
            # Single layer
            if hasattr(layer_data, 'empty') and not layer_data.empty:
                report_lines.append(f"- **Count:** {len(layer_data)}")
                if len(layer_data) > 0:
                    geom_type = layer_data.geometry.geom_type.iloc[0]
                    report_lines.append(f"- **Primary Geometry:** {geom_type}")
                    
                    # Show sample attributes
                    if hasattr(layer_data, 'columns'):
                        attr_cols = [c for c in layer_data.columns if c not in ['geometry']]
                        if attr_cols:
                            report_lines.append(f"- **Attributes:** {', '.join(attr_cols[:5])}")
                            if len(attr_cols) > 5:
                                report_lines.append(f"  - *... and {len(attr_cols) - 5} more*")
        report_lines.append("")
    
    # Write report
    report_content = "\n".join(report_lines)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"[i] Generated Markdown report: {output_path}")

def generate_reports(layers: Dict[str, Any], config: Dict[str, Any], output_dir: Path) -> None:
    """Generate both CSV summary and Markdown report."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate CSV summary
    csv_path = output_dir / "layer_summary.csv"
    generate_csv_summary(layers, csv_path)
    
    # Generate Markdown report
    md_path = output_dir / "processing_report.md"
    generate_markdown_report(layers, config, md_path)
