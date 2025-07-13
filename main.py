# Bootstrap and CLI parser for WallpaperScraper
import argparse
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Load environment variables early
from dotenv import load_dotenv
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="WallpaperScraper - Download ultra-high-resolution wallpapers from multiple sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --scrape --theme nature abstract
  python main.py --scout  # Explore available themes
  python main.py --theme "new york" --resolution 3840x2160
  python main.py --scrape --max-downloads 20 --output ./my_wallpapers
        """
    )
    
    # Version and basic options
    parser.add_argument(
        '--version',
        action='version',
        version='WallpaperScraper 1.1.0')
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom config file')
    
    # Main actions
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        '--scrape',
        action='store_true',
        help='Start wallpaper scraping')
    
    action_group.add_argument(
        '--scout',
        action='store_true',
        help='Explore wallpaper sites for available themes and categories')
    
    action_group.add_argument(
        '--investigate',
        type=str,
        metavar='SITE',
        help='Investigate specific site (e.g., wallpaperswide.com)')
    
    # Scraping options
    scrape_group = parser.add_argument_group('scraping options')
    scrape_group.add_argument(
        '--theme',
        type=str,
        nargs='*',
        help='One or more themes for wallpaper search (e.g., --theme nature city abstract, or --theme "new york" landscape)')
    
    scrape_group.add_argument(
        '--resolution',
        type=str,
        help='Desired wallpaper resolution (e.g., 5120x1440, 3840x1080)')
    
    scrape_group.add_argument(
        '--sites',
        type=str,
        nargs='*',
        choices=['wallpaperswide.com', 'wallhaven.cc', 'wallpaperbat.com'],
        help='Specific sites to scrape (default: all enabled sites)')
    
    scrape_group.add_argument(
        '--max-downloads',
        type=int,
        metavar='N',
        help='Maximum number of wallpapers to download per theme')
    
    scrape_group.add_argument(
        '--output',
        type=str,
        metavar='DIR',
        help='Output directory for downloaded wallpapers')
    
    # Performance options
    perf_group = parser.add_argument_group('performance options')
    perf_group.add_argument(
        '--workers',
        type=int,
        metavar='N',
        help='Number of parallel download workers')
    
    perf_group.add_argument(
        '--timeout',
        type=int,
        metavar='SEC',
        help='Request timeout in seconds')
    
    # Logging and debug options
    debug_group = parser.add_argument_group('debugging options')
    debug_group.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set logging level (default: INFO)')
    
    debug_group.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging with function names and line numbers')
    
    debug_group.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be downloaded without actually downloading')
    
    args = parser.parse_args()

    # Set up logging as early as possible
    import logging
    from src.utils import setup_enhanced_logging
    from pathlib import Path
    
    # Setup logging
    log_file = Path("temp/wallpaper_scraper.log") if not args.dry_run else None
    setup_enhanced_logging(
        log_level=args.log_level,
        log_file=log_file,
        include_debug=args.verbose
    )
    
    # Handle different actions
    if args.scout:
        logging.info("Starting wallpaper site exploration...")
        from src.wallpaper_scout import main as scout_main
        scout_main()
        
    elif args.investigate:
        logging.info(f"Investigating site: {args.investigate}")
        if args.investigate == 'wallpaperswide.com':
            from src.investigate_wallpaperswide import inspect_wallpaperswide
            inspect_wallpaperswide()
        else:
            logging.error(f"Investigation not implemented for site: {args.investigate}")
            sys.exit(1)
            
    elif args.scrape or args.theme:
        # Determine theme: from CLI or prompt
        themes = args.theme
        if not themes:
            theme_input = input('Enter themes for wallpaper search (separated by spaces, use quotes for multi-word themes): ').strip()
            if not theme_input:
                logging.error('At least one theme is required to proceed. For more options, run: python main.py --help')
                sys.exit(1)
            themes = theme_input.split()
        
        # Validate themes
        if not themes:
            logging.error('At least one theme is required for scraping')
            sys.exit(1)
        
        # Prepare scraping options
        scrape_options = {
            'themes': themes,
            'resolution': args.resolution,
            'sites': args.sites,
            'max_downloads': args.max_downloads,
            'output_dir': args.output,
            'workers': args.workers,
            'timeout': args.timeout,
            'dry_run': args.dry_run,
        }
        
        # Remove None values
        scrape_options = {k: v for k, v in scrape_options.items() if v is not None}
        
        logging.info(f"Starting wallpaper scraping with themes: {', '.join(themes)}")
        if args.dry_run:
            logging.info("DRY RUN MODE: No files will be downloaded")
            
        from src.wallpaper_scraper import main as scraper_main
        scraper_main(**scrape_options)
        
    else:
        parser.print_help()
        logging.info('Displayed help message to user.')


if __name__ == "__main__":
    main()
