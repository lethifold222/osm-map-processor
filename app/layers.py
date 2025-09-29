from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import geopandas as gpd
import pandas as pd
import osmnx as ox
import shapely

@dataclass(frozen=True)
class ExtractedLayers:
    roads: Optional[gpd.GeoDataFrame]
    buildings: Optional[gpd.GeoDataFrame]
    amenities: Dict[str, gpd.GeoDataFrame]
    pois: Dict[str, gpd.GeoDataFrame]
    waterways: Optional[gpd.GeoDataFrame]
    landuse: Dict[str, gpd.GeoDataFrame]

def extract_layers(osm_bundle: Dict[str, Any], wanted_amenities: List[str], wanted_pois: List[str]) -> ExtractedLayers:
    """Split raw OSM data into logical layers.

    - Roads: edges GeoDataFrame from the road graph (drive network)
    - Buildings: features with building=* tag
    - Amenities: subset of POIs by amenity type
    - POIs: subset by generic keys (e.g., 'bank', 'atm', ...)
    - Waterways: features with waterway=* tag
    - Landuse: features with landuse=* tag

    Returns a typed container (ExtractedLayers).
    """
    # Roads
    roads = None
    if "roads_graph" in osm_bundle:
        roads = ox.graph_to_gdfs(osm_bundle["roads_graph"], nodes=False, edges=True)
        # Keep columns that are commonly useful
        keep_cols = [c for c in ["highway", "name", "oneway", "length", "maxspeed"] if c in roads.columns]
        roads = roads[keep_cols + ["geometry"]] if keep_cols else roads[["geometry"]]

    # Buildings
    buildings = None
    if "buildings" in osm_bundle:
        b = osm_bundle["buildings"]
        if not isinstance(b, gpd.GeoDataFrame):
            b = gpd.GeoDataFrame(b, geometry="geometry", crs="EPSG:4326")
        b = b[b.geometry.notna()]
        # Ensure polygons only
        buildings = b[b.geometry.type.isin(["Polygon", "MultiPolygon"])].copy()
        keep_cols = [c for c in ["building", "name", "levels", "height"] if c in buildings.columns]
        buildings = buildings[keep_cols + ["geometry"]] if keep_cols else buildings[["geometry"]]

    # Amenities & POIs
    amenities: Dict[str, gpd.GeoDataFrame] = {}
    pois: Dict[str, gpd.GeoDataFrame] = {}

    if "pois" in osm_bundle:
        p = osm_bundle["pois"]
        if not isinstance(p, gpd.GeoDataFrame):
            p = gpd.GeoDataFrame(p, geometry="geometry", crs="EPSG:4326")
        p = p[p.geometry.notna()].copy()

        if "amenity" in p.columns:
            for a in wanted_amenities:
                subset = p[p["amenity"] == a].copy()
                if not subset.empty:
                    amenities[a] = subset[["amenity", "name", "geometry"] if "name" in subset.columns else ["amenity", "geometry"]]

        # Generic POI filter: we accept matches on 'amenity' or 'shop' or direct 'tag==True'
        for key in wanted_pois:
            if key in p.columns:
                # True/False tag presence
                subset = p[p[key].astype(str).str.lower().isin(["true", "yes", "1"])].copy()
                if not subset.empty:
                    pois[key] = subset[[key, "geometry"]]
            else:
                # fallback: check amenity / shop categories
                m = (p.get("amenity", pd.Series([None]*len(p))) == key) | (p.get("shop", pd.Series([None]*len(p))) == key)
                subset = p[m].copy()
                if not subset.empty:
                    # Prefer a 'label' column to unify downstream
                    subset["label"] = key
                    pois[key] = subset[["label", "geometry"]]

    # Waterways
    waterways = None
    if "pois" in osm_bundle:
        p = osm_bundle["pois"]
        if not isinstance(p, gpd.GeoDataFrame):
            p = gpd.GeoDataFrame(p, geometry="geometry", crs="EPSG:4326")
        p = p[p.geometry.notna()].copy()
        
        if "waterway" in p.columns:
            waterways_subset = p[p["waterway"].notna()].copy()
            if not waterways_subset.empty:
                keep_cols = [c for c in ["waterway", "name", "width", "tunnel", "bridge"] if c in waterways_subset.columns]
                waterways = waterways_subset[keep_cols + ["geometry"]] if keep_cols else waterways_subset[["waterway", "geometry"]]

    # Landuse
    landuse: Dict[str, gpd.GeoDataFrame] = {}
    if "pois" in osm_bundle:
        p = osm_bundle["pois"]
        if not isinstance(p, gpd.GeoDataFrame):
            p = gpd.GeoDataFrame(p, geometry="geometry", crs="EPSG:4326")
        p = p[p.geometry.notna()].copy()
        
        if "landuse" in p.columns:
            landuse_data = p[p["landuse"].notna()].copy()
            if not landuse_data.empty:
                # Group by landuse type
                for landuse_type in landuse_data["landuse"].unique():
                    if pd.notna(landuse_type):
                        subset = landuse_data[landuse_data["landuse"] == landuse_type].copy()
                        if not subset.empty:
                            keep_cols = [c for c in ["landuse", "name", "area"] if c in subset.columns]
                            landuse[str(landuse_type)] = subset[keep_cols + ["geometry"]] if keep_cols else subset[["landuse", "geometry"]]

    return ExtractedLayers(
        roads=roads, 
        buildings=buildings, 
        amenities=amenities, 
        pois=pois,
        waterways=waterways,
        landuse=landuse
    )

# TODO(cursor): implement deduplication & spatial index/caching.
