from __future__ import annotations
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
import geopandas as gpd
import osmnx as ox
import hashlib
import pickle
import time
from .osm_parser import load_osm_file

def ensure_dir(path: str | Path) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)

def _get_cache_key(bbox: Optional[Tuple[float, float, float, float]] = None, place: Optional[str] = None, osm_file: Optional[str] = None) -> str:
    """Generate cache key for OSM data."""
    if osm_file:
        # For OSM files, use file path and modification time
        file_path = Path(osm_file)
        if file_path.exists():
            mtime = file_path.stat().st_mtime
            key_data = f"{osm_file}:{mtime}"
        else:
            key_data = osm_file
    elif bbox:
        key_data = f"bbox:{bbox}"
    elif place:
        key_data = f"place:{place}"
    else:
        raise ValueError("No input specified")
    
    return hashlib.md5(key_data.encode()).hexdigest()

def _load_from_cache(cache_key: str, cache_dir: str, ttl_hours: int) -> Optional[Dict[str, Any]]:
    """Load OSM data from cache if available and not expired."""
    cache_file = Path(cache_dir) / f"{cache_key}.pkl"
    
    if not cache_file.exists():
        return None
    
    # Check if cache is expired
    cache_age_hours = (time.time() - cache_file.stat().st_mtime) / 3600
    if cache_age_hours > ttl_hours:
        cache_file.unlink()  # Remove expired cache
        return None
    
    try:
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    except Exception:
        cache_file.unlink()  # Remove corrupted cache
        return None

def _save_to_cache(data: Dict[str, Any], cache_key: str, cache_dir: str) -> None:
    """Save OSM data to cache."""
    cache_file = Path(cache_dir) / f"{cache_key}.pkl"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"Warning: Failed to save cache: {e}")

def load_osm_cached(bbox: Optional[Tuple[float, float, float, float]] = None, 
                   place: Optional[str] = None, 
                   osm_file: Optional[str] = None,
                   cache_enabled: bool = True,
                   cache_dir: str = ".cache",
                   ttl_hours: int = 24) -> Dict[str, Any]:
    """Load OSM data with caching support."""
    
    # Try to load from cache first
    if cache_enabled:
        cache_key = _get_cache_key(bbox, place, osm_file)
        cached_data = _load_from_cache(cache_key, cache_dir, ttl_hours)
        if cached_data is not None:
            print(f"[i] Loaded OSM data from cache: {cache_key}")
            return cached_data
    
    # Load fresh data
    data = load_osm(bbox, place, osm_file)
    
    # Save to cache
    if cache_enabled:
        cache_key = _get_cache_key(bbox, place, osm_file)
        _save_to_cache(data, cache_key, cache_dir)
        print(f"[i] Cached OSM data: {cache_key}")
    
    return data

def load_osm(bbox: Optional[Tuple[float, float, float, float]] = None, place: Optional[str] = None, osm_file: Optional[str] = None) -> Dict[str, Any]:
    """Load OSM data as GeoDataFrames.

    Returns a dict with potential keys: 'roads', 'buildings', 'pois'.
    """
    result: Dict[str, Any] = {}
    
    if osm_file:
        # Load from OSM file
        osm_data = load_osm_file(osm_file)
        
        # Convert OSM data to expected format
        if 'ways' in osm_data:
            # Filter ways by type for roads
            roads_ways = osm_data['ways']
            if 'highway' in roads_ways.columns:
                roads_ways = roads_ways[roads_ways['highway'].notna()]
            result['roads'] = roads_ways
            
            # Filter ways by type for buildings
            if 'building' in osm_data['polygons'].columns:
                buildings_polygons = osm_data['polygons']
                buildings_polygons = buildings_polygons[buildings_polygons['building'].notna()]
                result['buildings'] = buildings_polygons
            elif 'building' in roads_ways.columns:
                buildings_ways = roads_ways[roads_ways['building'].notna()]
                result['buildings'] = buildings_ways
        
        # POIs from polygons and ways
        pois_data = []
        for geom_type in ['ways', 'polygons', 'multipolygons']:
            if geom_type in osm_data:
                gdf = osm_data[geom_type]
                if 'amenity' in gdf.columns:
                    amenity_pois = gdf[gdf['amenity'].notna()]
                    pois_data.append(amenity_pois)
        
        if pois_data:
            result['pois'] = gpd.pd.concat(pois_data, ignore_index=True)
        
        return result
    
    elif bbox:
        # Roads/graphs
        G = ox.graph_from_bbox(bbox[3], bbox[1], bbox[2], bbox[0], network_type="drive")
        result["roads_graph"] = G
        # Buildings
        buildings = ox.geometries_from_bbox(bbox[3], bbox[1], bbox[2], bbox[0], {"building": True})
        result["buildings"] = buildings
        # POIs
        pois = ox.geometries_from_bbox(bbox[3], bbox[1], bbox[2], bbox[0], {"amenity": True})
        result["pois"] = pois
    elif place:
        G = ox.graph_from_place(place, network_type="drive")
        result["roads_graph"] = G
        buildings = ox.geometries_from_place(place, {"building": True})
        result["buildings"] = buildings
        pois = ox.geometries_from_place(place, {"amenity": True})
        result["pois"] = pois
    else:
        raise ValueError("Either bbox, place, or osm_file must be provided.")

    return result

def export_geodataframe(gdf: gpd.GeoDataFrame, path: str | Path, format: str = "geojson") -> None:
    """Export GeoDataFrame to various formats."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    format = format.lower()
    
    if format == "geojson":
        gdf.to_file(path, driver="GeoJSON")
    elif format == "geopackage":
        # For GeoPackage, we need to handle the path differently
        if path.suffix != ".gpkg":
            path = path.with_suffix(".gpkg")
        gdf.to_file(path, driver="GPKG", layer=path.stem)
    elif format == "parquet":
        # For Parquet, we need to handle the path differently
        if path.suffix != ".parquet":
            path = path.with_suffix(".parquet")
        gdf.to_parquet(path)
    else:
        raise ValueError(f"Unsupported format: {format}")

def export_geodataframe_multi(gdf: gpd.GeoDataFrame, base_path: str | Path, formats: list[str]) -> None:
    """Export GeoDataFrame to multiple formats."""
    base_path = Path(base_path)
    
    for format in formats:
        if format.lower() == "geojson":
            export_geodataframe(gdf, base_path.with_suffix(".geojson"), "geojson")
        elif format.lower() == "geopackage":
            export_geodataframe(gdf, base_path.with_suffix(".gpkg"), "geopackage")
        elif format.lower() == "parquet":
            export_geodataframe(gdf, base_path.with_suffix(".parquet"), "parquet")

def export_vector_map(layers: Dict[str, Any], output_dir: Path, formats: list[str]) -> None:
    """Export map layers to vector formats (SVG, PDF, EPS)."""
    from .visualize import create_vector_map
    
    for format_ext in formats:
        if format_ext.lower() in ['svg', 'pdf', 'eps']:
            output_path = output_dir / f"map.{format_ext}"
            create_vector_map(layers, output_path, format_ext.upper())

def export_raster_map(layers: Dict[str, Any], output_dir: Path, formats: list[str], dpi: int = 300) -> None:
    """Export map layers to raster formats (PNG, JPG)."""
    from .visualize import create_raster_map
    
    for format_ext in formats:
        if format_ext.lower() in ['png', 'jpg', 'jpeg']:
            output_path = output_dir / f"map.{format_ext}"
            create_raster_map(layers, output_path, format_ext.upper(), dpi=dpi)

# TODO(cursor): add GeoPackage export and parquet/feather
