import importlib.util
import os
import sys

SRC_PATH = os.path.join(os.path.dirname(__file__), '..', 'src')
if SRC_PATH not in sys.path:
    sys.path.insert(0, SRC_PATH)

import config  # noqa: E402


def test_config_has_required_keys():
    required_keys = [
        'RESOLUTION', 'SITES', 'OUTPUT_FOLDER', 'TEMP_FOLDER',
        'REQUEST_TIMEOUT', 'MAX_RETRIES', 'RETRY_DELAY', 'REQUEST_DELAY',
        'USER_AGENT', 'LOG_LEVEL', 'MAX_ITEMS_PER_THEME', 'MAX_WORKERS'
    ]
    for key in required_keys:
        assert key in config.CONFIG, f"Missing config key: {key}"
    # Check new global config objects
    assert hasattr(config, 'DEFAULT_HEADERS')
    assert isinstance(config.DEFAULT_HEADERS, dict)
    assert hasattr(config, 'SUPPORTED_IMAGE_FORMATS')
    assert isinstance(config.SUPPORTED_IMAGE_FORMATS, list)
    assert hasattr(config, 'PROGRESS_BAR_CONFIG')
    assert isinstance(config.PROGRESS_BAR_CONFIG, dict)
    assert hasattr(config, 'DEPRECATED_SITES')
    assert isinstance(config.DEPRECATED_SITES, list)


def test_available_services():
    assert isinstance(config.AVAILABLE_SERVICES, list)
    assert all(isinstance(s, str) for s in config.AVAILABLE_SERVICES)
