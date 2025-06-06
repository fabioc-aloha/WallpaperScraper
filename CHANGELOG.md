# Changelog

All notable changes to the WallpaperScraper project will be documented in this file.

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
