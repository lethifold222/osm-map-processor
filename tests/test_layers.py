from app.layers import extract_layers, ExtractedLayers
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, Polygon

def make_fake_bundle():
    roads_graph = None  # not used in this basic unit test
    buildings = gpd.GeoDataFrame({
        "building": ["yes", None],
        "name": ["A", "B"],
        "geometry": [Polygon([(0,0), (1,0), (1,1), (0,1)]), Point(0,0)],  # only first is polygon
    }, crs="EPSG:4326")

    pois = gpd.GeoDataFrame({
        "amenity": ["school", "hospital", "restaurant", None],
        "shop": [None, None, "bakery", "supermarket"],
        "geometry": [Point(0.1, 0.1), Point(0.2, 0.2), Point(0.3, 0.3), Point(0.4, 0.4)],
    }, crs="EPSG:4326")

    return {"buildings": buildings, "pois": pois}

def test_extract_layers_basic():
    bundle = make_fake_bundle()
    layers = extract_layers(bundle, wanted_amenities=["school", "hospital"], wanted_pois=["bank", "supermarket"])
    assert isinstance(layers, ExtractedLayers)
    assert "school" in layers.amenities
    assert "hospital" in layers.amenities
    assert "supermarket" in layers.pois
    assert "bank" not in layers.pois  # not present in fake data
