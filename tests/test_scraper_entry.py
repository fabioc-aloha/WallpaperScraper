import importlib
import sys
import os

SRC_PATH = os.path.join(os.path.dirname(__file__), '..', 'src')
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)


def test_wallpaper_scraper_import():
    importlib.import_module('wallpaper_scraper')


def test_wallpaper_scout_import():
    importlib.import_module('wallpaper_scout')
