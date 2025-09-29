from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from typing import List, Optional, Dict
import yaml
from pathlib import Path

class InputSpec(BaseModel):
    bbox: Optional[List[float]] = Field(default=None, description="[minx, miny, maxx, maxy]")
    place: Optional[str] = None
    osm_file: Optional[str] = Field(default=None, description="Path to .osm file to load")

class OutputSpec(BaseModel):
    output_dir: str = "./outputs"
    overwrite: bool = True
    vector_formats: List[str] = Field(default_factory=lambda: ["svg", "pdf"], description="Vector formats to export: svg, pdf, eps")
    image_formats: List[str] = Field(default_factory=lambda: ["png"], description="Raster formats to export: png, jpg")
    geodata_formats: List[str] = Field(default_factory=lambda: ["geojson"], description="Geodata formats: geojson, geopackage, parquet")
    enable_reports: bool = True

class LayerSelection(BaseModel):
    roads: bool = True
    buildings: bool = True
    waterways: bool = True
    amenities: List[str] = Field(default_factory=lambda: ["school", "hospital"])
    pois: List[str] = Field(default_factory=lambda: ["bank", "atm"])
    landuse: List[str] = Field(default_factory=lambda: ["residential", "commercial", "industrial", "park"])

class CRSOptions(BaseModel):
    target_epsg: int = 3857

class VizOptions(BaseModel):
    quick_preview: bool = True
    sample_n: int = 1000
    map_style: str = "osm"  # "osm", "minimal", "custom"
    background_color: str = "#f5f5f3"
    custom_colors: Dict[str, str] = Field(default_factory=dict)
    osm_style: bool = True

class CacheOptions(BaseModel):
    enable_cache: bool = True
    cache_dir: str = ".cache"
    cache_ttl_hours: int = 24

class AppConfig(BaseSettings):
    project_name: str = "cursor_osm_project"
    input: InputSpec = InputSpec()
    output: OutputSpec = OutputSpec()
    layers: LayerSelection = LayerSelection()
    crs: CRSOptions = CRSOptions()
    visualize: VizOptions = VizOptions()
    cache: CacheOptions = CacheOptions()

    @staticmethod
    def from_yaml(path: str | Path) -> "AppConfig":
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return AppConfig(**data)
