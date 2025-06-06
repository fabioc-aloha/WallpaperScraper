# Bootstrap and CLI parser for WallpaperScraper
import argparse
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def main():
    parser = argparse.ArgumentParser(description="Wallpaper Scraper CLI")
    parser.add_argument(
        '--version',
        action='version',
        version='WallpaperScraper 1.0.0')
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom config file')
    parser.add_argument(
        '--scrape',
        action='store_true',
        help='Start wallpaper scraping')
    parser.add_argument(
        '--theme',
        type=str,
        nargs='*',
        help='One or more themes for wallpaper search (e.g., --theme nature city abstract, or --theme "new york" landscape)')
    parser.add_argument(
        '--resolution',
        type=str,
        help='Desired wallpaper resolution (e.g., 5120x1440, 3840x1080)')
    parser.add_argument(
        '--log-level',
        type=str,
        default='ERROR',
        help='Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Default is ERROR.'
    )
    # Add more CLI options as needed
    args = parser.parse_args()

    # Set up logging as early as possible
    import logging
    log_level = args.log_level.upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )    # Only proceed if scraping is requested
    if args.scrape or args.theme:
        # Determine theme: from CLI or prompt
        themes = args.theme
        if not themes:
            theme_input = input('Enter themes for wallpaper search (separated by spaces, use quotes for multi-word themes): ').strip()
            if not theme_input:
                logging.error('At least one theme is required to proceed. For more options, run: python main.py --help')
                sys.exit(1)
            themes = theme_input.split()
        # Determine resolution: from CLI or config
        resolution = args.resolution if args.resolution else None
        # Determine log level: from CLI or config
        log_level = args.log_level.upper() if args.log_level else None
        from src.wallpaper_scraper import main as scraper_main
        scraper_main(log_level=log_level, themes=themes, resolution=resolution)
    else:
        parser.print_help()
        logging.info('Displayed help message to user.')


if __name__ == "__main__":
    main()
