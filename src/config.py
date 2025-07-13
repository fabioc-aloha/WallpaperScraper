"""
config.py

Centralized configuration for the Wallpaper Scraper application.
Defines all runtime, scraper, and storage settings in one place.
Supports environment variable overrides via .env file.
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Helper functions for environment variable handling
def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean environment variable with default fallback."""
    return os.getenv(key, str(default)).lower() in ('true', '1', 'yes', 'on')


def get_env_int(key: str, default: int) -> int:
    """Get integer environment variable with default fallback."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        logging.warning(f"Invalid integer value for {key}, using default: {default}")
        return default


def get_env_float(key: str, default: float) -> float:
    """Get float environment variable with default fallback."""
    try:
        return float(os.getenv(key, str(default)))
    except ValueError:
        logging.warning(f"Invalid float value for {key}, using default: {default}")
        return default


def get_env_list(key: str, default: List[str], separator: str = ',') -> List[str]:
    """Get list environment variable with default fallback."""
    value = os.getenv(key)
    if value:
        return [item.strip() for item in value.split(separator) if item.strip()]
    return default


# Base data directory for storing downloaded wallpapers
# Can be overridden by DEFAULT_DOWNLOAD_DIR environment variable
default_data_dir = os.getenv('DEFAULT_DOWNLOAD_DIR', r'C:\Data')
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
    'VERSION': '1.0.2',  # Project version (updated for enhancements)
    'RESOLUTION': os.getenv('DEFAULT_RESOLUTION', '5120x1440'),  # Desired wallpaper resolution
    'SITES': get_env_list('ENABLED_SITES', [
        'wallpaperswide.com',
        'wallhaven.cc',
        'wallpaperbat.com'
    ]),
    
    # Storage Folders
    'OUTPUT_FOLDER': os.path.join(default_data_dir, 'wallpapers'),  # Where wallpapers are saved
    'TEMP_FOLDER': os.path.join(PROJECT_ROOT, 'temp'),  # For logs and temp files

    # HTTP Settings
    'REQUEST_TIMEOUT': get_env_int('REQUEST_TIMEOUT', 30),  # Increased from env or default
    'MAX_RETRIES': get_env_int('MAX_RETRIES', 3),       # Number of retry attempts
    'RETRY_DELAY': get_env_float('RETRY_DELAY', 1.0),     # Delay between retries (seconds)
    'REQUEST_DELAY': get_env_float('REQUEST_DELAY', 2.0),   # Delay between requests to the same site
    'USER_AGENT': os.getenv('USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'),
    'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO').upper(),    # Logging level from env
    'MAX_ITEMS_PER_THEME': get_env_int('MAX_ITEMS_PER_THEME', 10),  # Max wallpapers to process per theme

    # Parallelism
    'MAX_WORKERS': get_env_int('MAX_CONCURRENT_DOWNLOADS', 4),        # From env or default
    
    # Debug and Development
    'DEBUG': get_env_bool('DEBUG', False),  # Debug mode flag
    
    # Site-specific configurations
    'WALLHAVEN_API_KEY': os.getenv('WALLHAVEN_API_KEY', ''),  # Optional API key for enhanced access
    'WALLPAPERBAT_USER_AGENT': os.getenv('WALLPAPERBAT_USER_AGENT', 'WallpaperScraper/1.0'),
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
