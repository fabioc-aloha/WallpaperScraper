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

## Project Evolution

This project has evolved through careful consideration of various challenges and solutions. We maintain two key documents that not only track our journey but also help GitHub Copilot provide better assistance:

1. `DECISIONS.md` - Contains architectural decisions that require explicit user approval to change. This helps GitHub Copilot understand and respect the project's core design principles.

2. `LEARNINGS.md` - Automatically updated by GitHub Copilot as it helps solve problems, documenting successful approaches and preventing repetition of unsuccessful strategies.

### Design Decisions (`DECISIONS.md`)

Key architectural decisions include:
- Multi-service architecture for resilience against site changes
- Sophisticated resolution matching system with quality levels
- Parallel processing with intelligent retry mechanisms
- Centralized configuration for easy customization

See [`DECISIONS.md`](DECISIONS.md) for detailed rationales behind these and other architectural choices.

### Project Learnings (`LEARNINGS.md`)

Notable learnings from development include:
- Website scraping challenges and solutions
- Service-specific adaptations
- Performance optimization techniques
- Error handling strategies
- Testing approaches

Our [`LEARNINGS.md`](LEARNINGS.md) document captures these experiences in detail, helping future contributors understand:
- What worked well
- What didn't work
- How we solved specific challenges
- Ongoing improvements

### Integration with GitHub Copilot

These documents serve a dual purpose:

1. **Human Documentation**: They provide valuable context for users and contributors about the project's evolution and rationale.

2. **AI Assistance**: They help GitHub Copilot:
   - Understand and respect architectural boundaries
   - Learn from past solutions and challenges
   - Make informed suggestions aligned with project principles
   - Avoid repeating approaches that didn't work
   - Document new solutions as they're implemented

`DECISIONS.md` acts as a guardrail, requiring explicit user approval for architectural changes, while `LEARNINGS.md` serves as GitHub Copilot's dynamic knowledge base, continuously updated as it assists with problem-solving.

## License

MIT License — see `LICENSE` for details.