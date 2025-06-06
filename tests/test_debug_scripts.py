import importlib
import sys
import os
import pytest

SRC_PATH = os.path.join(os.path.dirname(__file__), '..', 'src')
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

debug_scripts = [
    'debug_site_structure',
    'investigate_wallpapers',
    'investigate_wallpaperswide',
]


@pytest.mark.parametrize("modname", debug_scripts)
def test_debug_script_imports(modname):
    importlib.import_module(modname)
