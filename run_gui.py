#!/usr/bin/env python3
"""
Simple launcher for the OSM Map Processor GUI.
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

# Change to app directory
os.chdir(app_dir)

# Import and run
try:
    from gui import main
    main()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
