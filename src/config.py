"""
config.py

Centralized configuration for the Wallpaper Scraper application.
Defines all runtime, scraper, and storage settings in one place.
"""

import os

# Base data directory for storing downloaded wallpapers
# Change this to your preferred location
default_data_dir = r'C:\Data'
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

AVAILABLE_SERVICES = [
    'wallpaperswide.com',
    'wallhaven.cc',
    'wallpaperbat.com',
    # Deprecated: 'ultrawidewallpapers.net',
    # Deprecated: '4kwallpapers.com',
    # Deprecated: 'wallpapercave.com',
    # Deprecated: 'wallpapers.com/widescreen'
]

CONFIG = {
    # Wallpaper Settings
    'VERSION': '1.0.0',  # Project version
    'RESOLUTION': '5120x1440',  # Desired wallpaper resolution (width x height)
    'SITES': [
        'wallpaperswide.com',
        'wallhaven.cc',
        'wallpaperbat.com'
    ],
    # Deprecated sites: '4kwallpapers.com' - no longer working with our implementation

    # Storage Folders
    'OUTPUT_FOLDER': os.path.join(default_data_dir, 'wallpapers'),  # Where wallpapers are saved
    'TEMP_FOLDER': os.path.join(PROJECT_ROOT, 'temp'),  # For logs and temp files

    # HTTP Settings
    'REQUEST_TIMEOUT': 10,  # Timeout for HTTP requests (seconds)
    'MAX_RETRIES': 3,       # Number of retry attempts
    'RETRY_DELAY': 1.0,     # Delay between retries (seconds)
    'REQUEST_DELAY': 2.0,   # Delay between requests to the same site (seconds)
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'LOG_LEVEL': 'INFO',    # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    'MAX_ITEMS_PER_THEME': 10,  # Max wallpapers to process per theme

    # Parallelism
    'MAX_WORKERS': 4,        # Number of parallel download workers
}

DEFAULT_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

SUPPORTED_IMAGE_FORMATS = ['jpg', 'jpeg', 'png']

PROGRESS_BAR_CONFIG = {
    'bar_format': '{l_bar}{bar}| {n_fmt}/{total_fmt} {desc}',
    'leave': True
}

DEPRECATED_SITES = [
    'ultrawidewallpapers.net',
    '4kwallpapers.com',
    'wallpapercave.com',
    'wallpapers.com/widescreen'
]
