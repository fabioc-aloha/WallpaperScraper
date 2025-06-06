import sys
import os
# Add the root directory and src directory to the Python path
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC_PATH = os.path.join(ROOT_PATH, 'src')
for path in [ROOT_PATH, SRC_PATH]:
    if path not in sys.path:
        sys.path.insert(0, path)
from services import wallhaven_service
from services import wallpaperbat_service
from services import wallpaperswide_service
import config


def test_services_use_default_headers():
    for svc_cls in [wallhaven_service.WallhavenService, wallpaperbat_service.WallpaperBatService, wallpaperswide_service.WallpapersWideService]:
        svc = svc_cls(resolution="5120x1440", themes=["nature"])
        for k, v in config.DEFAULT_HEADERS.items():
            assert svc.headers[k] == v
        assert svc.headers['User-Agent'] == config.CONFIG['USER_AGENT']
