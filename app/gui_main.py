#!/usr/bin/env python3
"""
Main entry point for the OSM Map Processor GUI application.
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Change to app directory to make relative imports work
os.chdir(app_dir)

from gui import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)
