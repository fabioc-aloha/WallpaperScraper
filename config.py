"""Global Configuration for Wallpaper Scraper

This module provides centralized configuration for the wallpaper scraper application.
All configurable parameters are defined here to allow easy customization.
"""

import os

# Base data directory for storing downloaded wallpapers
default_data_dir = r'C:\Data'
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

CONFIG = {    # Wallpaper Settings
    'RESOLUTION': '5120x1440',                     # Desired wallpaper resolution (width x height)
    'THEMES': ['Abstract', 'digital'],              # Themes for wallpaper search
    'SITES': ['wallpaperswide.com', 'wallhaven.cc', 'wallpaperbat.com'], # Wallpaper sites to fetch from
    # Deprecated sites: '4kwallpapers.com' - no longer working with our implementation

    # Storage Folders
    'OUTPUT_FOLDER': os.path.join(default_data_dir, 'wallpapers'),
    'TEMP_FOLDER': os.path.join(PROJECT_ROOT, 'temp'),

    # HTTP Settings
    'REQUEST_TIMEOUT': 10,                          # Timeout for HTTP requests
    'MAX_RETRIES': 3,                               # Number of retry attempts
    'RETRY_DELAY': 1.0,                             # Delay between retries (seconds)
    'REQUEST_DELAY': 2.0,                           # Delay between requests to the same site (seconds)
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'LOG_LEVEL': 'INFO',                            # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    'MAX_ITEMS_PER_THEME': 10,                      # Maximum number of items to process per theme

    # Parallelism
    'MAX_WORKERS': 4                                # Number of parallel download workers
}