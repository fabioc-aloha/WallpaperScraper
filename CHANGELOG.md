# Changelog

All notable changes to the WallpaperScraper project will be documented in this file.

## [1.0.1] - June 28, 2025

### Removed
- **Dead code cleanup**: Removed deprecated 4kwallpapers.com investigation scripts
  - Deleted `src/investigate_wallpapers.py` (targeted deprecated site)
  - Deleted `src/debug_site_structure.py` (targeted deprecated site)
  - Removed empty duplicate `services/` directory from root
  - Cleaned up unnecessary `.gitkeep` files
  - Removed empty `src/services/__init__.py`

### Fixed
- **Import path corrections**: Updated all service imports to use proper `src.` paths
  - Fixed `wallpaper_scout.py` import paths
  - Updated test imports in `test_services_import.py`
  - Corrected service file imports to use `src.config`
- **Test suite improvements**: 
  - Fixed `test_debug_scripts.py` to only test existing scripts
  - Corrected `test_multiple_themes.py` assertions to match actual log output format
- **Documentation updates**: Updated README.md to remove references to deleted debug scripts

### Improved
- **Dependencies**: Revised `requirements.txt` with proper version constraints and documentation
  - Added version minimums for core dependencies
  - Organized dependencies by purpose with clear comments
  - Removed unused `autopep8` dependency
- **Git ignore**: Enhanced `.gitignore` with comprehensive patterns
  - Better cross-platform OS support
  - Enhanced IDE/editor patterns
  - Added project-specific ignore patterns for wallpaper storage
  - Improved organization with clear section headers

### Technical Details
- All Python cache directories cleaned up
- Import paths now consistently use `src.` prefix
- Test suite validates remaining functionality
- Project structure simplified and more maintainable

## [1.0.0] - June 2025

### Added
- Support for multiple themes via CLI argument: `--theme nature abstract city`
- Support for multi-word themes using quotes: `--theme "new york" landscape`
- Interactive theme input with multiple theme support
- Process-based progress tracking for more accurate progress reporting
- Service-specific progress steps for better accuracy
- Support for conditional progress steps (e.g., ultrawide search)

### Changed
- Updated progress tracking to use process steps instead of item counts
- Modified progress calculations to be theme-based
- Improved documentation for multi-theme usage
- Each service now defines its own process steps for progress tracking
- Progress reporting now happens at natural process boundaries

### Fixed
- Progress reporting for unknown total items
- Progress accuracy for multi-stage processes
- Progress display for conditional steps (e.g., ultrawide search)
