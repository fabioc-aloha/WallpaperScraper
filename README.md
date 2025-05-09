# Ultra-Resolution Wallpaper Scraper

A Python utility that downloads ultra-high-resolution wallpapers directly from configured wallpaper sites, with support for themes, pagination, and parallel processing.

## Key Features

- Fetches wallpapers by theme from multiple reputable sources:
  - wallpaperswide.com
  - wallhaven.cc
  - wallpaperbat.com (with specialized support for 5120x1440 super ultrawide wallpapers)
- Supports configurable resolution (default: 5120×1440)
- Sophisticated image resolution verification:
  - Exact match detection (ideal case)
  - Similar aspect ratio with higher resolution
  - Larger resolution with any aspect ratio
  - Automatic removal of undersized images
- Smart file skipping based on both filename and resolution requirements
- Parallel downloads with intelligent retry logic and exponential backoff
- Robust error handling and detailed logging
- Clean, centralized configuration in `config.py`
- Adaptive scraping techniques that handle website structure changes
- Designed to run on Windows PowerShell

## Requirements

Install dependencies in a virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

All settings are in `config.py`:
- `RESOLUTION`: Desired wallpaper size
- `THEMES`: List of search themes
- `SITES`: Wallpaper sites to fetch from
- `OUTPUT_FOLDER`, `TEMP_FOLDER` paths
- HTTP settings and parallelism controls

## Usage

Run the scraper in PowerShell:
```powershell
python wallpaper_scraper.py
```

Downloaded wallpapers are saved under the configured `OUTPUT_FOLDER`.

## Resolution Verification

The scraper uses a sophisticated resolution matching system with four quality levels:

1. **Exact Match (Level 3)**
   - Image dimensions match the target resolution within 5% tolerance
   - Ideal for maintaining consistent wallpaper collection

2. **Similar Aspect Ratio (Level 2)**
   - Larger resolution than target
   - Aspect ratio within 10% of target
   - Good for high-quality alternatives

3. **Larger Resolution (Level 1)**
   - Exceeds target dimensions
   - Different aspect ratio
   - Acceptable when exact matches unavailable

4. **Insufficient (Level 0)**
   - Smaller than target resolution
   - Automatically removed to maintain quality

This system ensures you get the best possible wallpapers while maintaining flexibility when exact matches aren't available.

## Running Tests

To run the test suite:
```powershell
python -m pytest tests/
```

The test suite covers:
- Download functionality with mock HTTP responses
- Resolution verification with various image sizes
- Error handling and retry logic
- Service-specific functionality for each wallpaper site

For development, you can also run individual test files:
```powershell
python -m pytest tests/test_wallpaper_scraper.py
python -m pytest tests/test_wallpaperbat_service.py
```

## Architecture

Decisions and architectural rationale are documented in `DECISIONS.md`.

## License

MIT License — see `LICENSE` for details.