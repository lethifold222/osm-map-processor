from __future__ import annotations
from typing import Dict, Any
from pathlib import Path
import geopandas as gpd
import pyproj

from .config import AppConfig
from .io import load_osm_cached, ensure_dir, export_geodataframe_multi, export_vector_map, export_raster_map
from .layers import extract_layers
from .visualize import preview_gdf, preview_layers
from .reports import generate_reports

def reproject(gdf: gpd.GeoDataFrame, target_epsg: int) -> gpd.GeoDataFrame:
    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=4326, allow_override=True)
    return gdf.to_crs(epsg=target_epsg)

def run_pipeline(cfg: AppConfig, verbose: bool = False) -> None:
    out_dir = Path(cfg.output.output_dir)
    ensure_dir(out_dir)

    if verbose:
        print(f"[i] Loading OSM for project '{cfg.project_name}' ...")

    osm_bundle: Dict[str, Any] = load_osm_cached(
        bbox=tuple(cfg.input.bbox) if cfg.input.bbox else None,
        place=cfg.input.place,
        osm_file=cfg.input.osm_file,
        cache_enabled=cfg.cache.enable_cache,
        cache_dir=cfg.cache.cache_dir,
        ttl_hours=cfg.cache.cache_ttl_hours,
    )

    if verbose:
        print("[i] Extracting layers ...")

    layers = extract_layers(osm_bundle, cfg.layers.amenities, cfg.layers.pois)

    # Reproject
    if verbose:
        print(f"[i] Reprojecting to EPSG:{cfg.crs.target_epsg} ...")

    if layers.roads is not None:
        layers.roads = reproject(layers.roads, cfg.crs.target_epsg)
    if layers.buildings is not None:
        layers.buildings = reproject(layers.buildings, cfg.crs.target_epsg)
    if layers.waterways is not None:
        layers.waterways = reproject(layers.waterways, cfg.crs.target_epsg)

    repro_amenities = {k: reproject(v, cfg.crs.target_epsg) for k, v in layers.amenities.items()}
    repro_pois = {k: reproject(v, cfg.crs.target_epsg) for k, v in layers.pois.items()}
    repro_landuse = {k: reproject(v, cfg.crs.target_epsg) for k, v in layers.landuse.items()}

    # Export
    if verbose:
        print("[i] Exporting ...")

    if layers.roads is not None and not layers.roads.empty:
        export_geodataframe(layers.roads, out_dir / "roads.geojson")
    if layers.buildings is not None and not layers.buildings.empty:
        export_geodataframe(layers.buildings, out_dir / "buildings.geojson")
    for name, gdf in repro_amenities.items():
        export_geodataframe(gdf, out_dir / f"amenity_{name}.geojson")
    for name, gdf in repro_pois.items():
        export_geodataframe(gdf, out_dir / f"poi_{name}.geojson")
    
    # Export vector and raster maps
    if cfg.output.vector_formats or cfg.output.image_formats:
        if verbose:
            print("[i] Exporting vector/raster maps ...")
        
        # Prepare layers for visualization
        viz_layers = {}
        if layers.roads is not None and not layers.roads.empty:
            viz_layers['roads'] = layers.roads
        if layers.buildings is not None and not layers.buildings.empty:
            viz_layers['buildings'] = layers.buildings
        viz_layers.update(repro_amenities)
        viz_layers.update(repro_pois)
        
        # Export vector formats
        if cfg.output.vector_formats:
            export_vector_map(viz_layers, out_dir, cfg.output.vector_formats)
        
        # Export raster formats
        if cfg.output.image_formats:
            export_raster_map(viz_layers, out_dir, cfg.output.image_formats)

    # Visualize (optional)
    if cfg.visualize.quick_preview:
        if verbose:
            print("[i] Generating quick previews ...")
        if layers.roads is not None:
            preview_gdf(layers.roads, title="Roads", sample_n=cfg.visualize.sample_n)
        if layers.buildings is not None:
            preview_gdf(layers.buildings, title="Buildings", sample_n=cfg.visualize.sample_n)
        preview_layers(repro_amenities, sample_n=cfg.visualize.sample_n)
        preview_layers(repro_pois, sample_n=cfg.visualize.sample_n)

    if verbose:
        print(f"[✓] Done. Outputs at: {out_dir.resolve()}")

# TODO(cursor): add metrics (counts per layer), CSV summary, and a small HTML report.
