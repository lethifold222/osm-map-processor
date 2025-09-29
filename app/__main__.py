import sys
from .cli import app

def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        # Launch GUI
        from .gui import main as gui_main
        gui_main()
    else:
        # Launch CLI
        app()

if __name__ == "__main__":
    main()
