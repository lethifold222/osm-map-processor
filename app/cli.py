from __future__ import annotations
import typer
from typing import Optional
from pathlib import Path
from .config import AppConfig
from .osm_pipeline import run_pipeline

app = typer.Typer(add_completion=False, no_args_is_help=True, help="Cursor OSM Pipeline")

@app.command("run")
def run(
    config: Path = typer.Option(..., "--config", exists=True, readable=True, help="Path to YAML config"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose logging"),
):
    """Run the OSM pipeline using a YAML config file."""
    cfg = AppConfig.from_yaml(config)
    run_pipeline(cfg, verbose=verbose)

@app.command("init-config")
def init_config(
    path: Path = typer.Option("example_config.yaml", "--path", help="Where to write a starter config"),
):
    """Write a starter config to disk."""
    from .config import AppConfig
    import yaml
    cfg = AppConfig()
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(cfg.model_dump(), f, allow_unicode=True, sort_keys=False)
    typer.echo(f"Wrote starter config to {path}")

@app.command("gui")
def launch_gui():
    """Launch the graphical user interface."""
    try:
        from .gui import main as gui_main
        gui_main()
    except ImportError as e:
        typer.echo(f"Error: GUI dependencies not available: {e}", err=True)
        typer.echo("Please install required packages: pip install -r requirements.txt", err=True)
        raise typer.Exit(1)
