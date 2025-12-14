#!/usr/bin/env python3
"""
Quick start script for the Wallpaper Scraper.
This script helps you get started quickly.
"""

import sys
import os

def main():
    print("=" * 60)
    print("Wallpaper Scraper - Quick Start")
    print("=" * 60)
    print()
    
    # Check if dependencies are installed
    try:
        import requests
        import PIL
        import bs4
        import aiohttp
        import tqdm
        import validators
        print("✓ All dependencies are installed")
    except ImportError as e:
        print("✗ Missing dependencies!")
        print()
        print("Please install dependencies first:")
        print("  pip install -r requirements.txt")
        print()
        return 1
    
    print()
    print("Choose an interface:")
    print("  1. GUI (Graphical Interface)")
    print("  2. CLI (Command Line)")
    print("  3. Show Examples")
    print("  4. Exit")
    print()
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == '1':
        print()
        print("Starting GUI...")
        print("Note: If you see an error, tkinter might not be installed.")
        print("      Install it with: apt-get install python3-tk (Linux)")
        print()
        try:
            import gui
            gui.main()
        except ImportError as e:
            print(f"Error: {e}")
            print("GUI requires tkinter. Try the CLI instead (option 2)")
            return 1
    
    elif choice == '2':
        print()
        print("CLI Help:")
        print("-" * 60)
        import subprocess
        subprocess.run([sys.executable, 'cli.py', '--help'])
        print()
        print("Examples:")
        print("  python cli.py -u https://example.com/image.jpg")
        print("  python cli.py -f example-urls.txt")
        print()
    
    elif choice == '3':
        print()
        print("Examples:")
        print("-" * 60)
        print()
        print("1. Download from direct URLs:")
        print("   python cli.py -u https://example.com/wallpaper1.jpg \\")
        print("                    https://example.com/wallpaper2.jpg")
        print()
        print("2. Download from a file:")
        print("   python cli.py -f example-urls.txt")
        print()
        print("3. Extract images from a webpage:")
        print("   python cli.py -p https://example.com/wallpapers-gallery")
        print()
        print("4. Download with custom filters:")
        print("   python cli.py -f urls.txt \\")
        print("                 --min-width 2560 \\")
        print("                 --min-height 1440 \\")
        print("                 --concurrent 10")
        print()
        print("5. Start GUI:")
        print("   python gui.py")
        print()
    
    elif choice == '4':
        print("Goodbye!")
        return 0
    
    else:
        print("Invalid choice. Please run the script again.")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
