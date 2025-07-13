"""
wallpaper_scraper.py

Main orchestration module for downloading ultra-high-resolution wallpapers from multiple sources.
Handles configuration, parallel downloads, resolution verification, and logging.
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from tqdm import tqdm
import logging
import time
import sys
from PIL import Image  # For checking image dimensions

from src.config import CONFIG, PROGRESS_BAR_CONFIG
from src.services.wallpaperswide_service import WallpapersWideService
from src.services.wallhaven_service import WallhavenService
from src.services.wallpaperbat_service import WallpaperBatService


def evaluate_resolution_match(width, height, target_width, target_height):
    """
    Evaluate how well an image matches the desired resolution.
    Returns a match code (0-3) for filtering and quality ranking.

    Args:
        width (int): Actual width of the image
        height (int): Actual height of the image
        target_width (int): Desired width
        target_height (int): Desired height

    Returns:
        int: Match code indicating the quality of the resolution match:
            3 - Exact match (perfect)
            2 - Greater resolution with similar aspect ratio (good)
            1 - Greater resolution with any aspect ratio (acceptable)
            0 - Smaller resolution (unacceptable)
    """
    # Calculate aspect ratios (with a small epsilon to avoid division by zero)
    epsilon = 0.0001
    target_ratio = target_width / max(target_height, epsilon)
    actual_ratio = width / max(height, epsilon)

    # Check for exact match (allowing a small 5% tolerance)
    width_match = 0.95 <= width / target_width <= 1.05
    height_match = 0.95 <= height / target_height <= 1.05
    if width_match and height_match:
        return 3  # Exact match

    # Check if greater resolution with similar aspect ratio
    # Aspect ratio within 10% of target is considered similar
    ratio_match = 0.9 <= (actual_ratio / target_ratio) <= 1.1
    greater_res = width >= target_width and height >= target_height
    if greater_res and ratio_match:
        return 2  # Greater resolution with similar aspect ratio

    # Check if any greater resolution
    if width >= target_width and height >= target_height:
        return 1  # Greater resolution but aspect ratio differs

    # Smaller resolution
    return 0  # Unacceptable


def check_image_resolution(filepath, min_width, min_height):
    """
    Check if an image file meets the minimum resolution requirements.
    Returns a tuple: (meets_requirement, width, height, match_code)

    Args:
        filepath (str): Path to the image file
        min_width (int): Minimum required width in pixels
        min_height (int): Minimum required height in pixels

    Returns:
        tuple: (meets_requirement (bool), actual_width (int), actual_height (int), match_code (int))
            match_code values:
            - 3: Exact match
            - 2: Greater resolution with similar aspect ratio
            - 1: Greater resolution with any aspect ratio
            - 0: Smaller resolution (unacceptable)
    """
    try:
        with Image.open(filepath) as img:
            width, height = img.size

            # Calculate how well the image matches our requirements
            match_code = evaluate_resolution_match(
                width, height, min_width, min_height)

            # Return whether it meets any of our acceptance criteria
            meets_requirement = match_code > 0
            return (meets_requirement, width, height, match_code)
    except Exception as e:
        logging.error(f"Error checking image resolution for {filepath}: {e}")
        return (False, 0, 0, 0)


def download_image(
        url,
        output_folder,
        timeout,
        retries,
        delay,
        headers,
        min_width=0,
        min_height=0):
    """
    Download a single image with retry logic, resolution check, and logging.
    Returns True if successful or already exists with correct resolution.

    Args:
        url (str): URL of the image to download
        output_folder (str): Folder to save the image
        timeout (int): Request timeout in seconds
        retries (int): Number of retry attempts
        delay (int): Base delay between retries (will be multiplied by attempt number)
        headers (dict): HTTP headers to use for the request
        min_width (int): Minimum required width in pixels
        min_height (int): Minimum required height in pixels

    Returns:
        bool: True if download was successful or file already exists with correct resolution, False otherwise
    """
    # Extract filename from URL and sanitize it
    filename = os.path.basename(url)
    # Replace any potentially problematic characters
    filename = filename.replace("?", "_").replace("&", "_")

    filepath = os.path.join(output_folder, filename)

    # Check if file already exists and has the correct resolution
    if os.path.exists(filepath):
        if min_width > 0 and min_height > 0:
            meets_req, width, height, match_code = check_image_resolution(
                filepath, min_width, min_height)
            if meets_req:
                match_type = {
                    3: "exact match",
                    2: "similar aspect ratio",
                    1: "larger resolution"}
                logging.info(
                    f"Skipping download of {filename} as it already exists with resolution ({width}x{height}), {match_type.get(match_code, 'acceptable')} for target {min_width}x{min_height}")
                return True
            else:
                logging.warning(
                    f"File {filename} exists but has insufficient resolution ({width}x{height}), re-downloading")
                # Continue with download to replace the file
        else:
            logging.info(
                f"Skipping download of {filename} as it already exists (resolution not checked)")
            return True

    for attempt in range(1, retries + 1):
        try:
            logging.debug(f"Downloading {url} (attempt {attempt}/{retries})")
            response = requests.get(url, timeout=timeout, headers=headers)

            if response.status_code == 200:
                # Save the file
                with open(filepath, "wb") as f:
                    f.write(response.content)

                # Verify the downloaded image has the correct resolution
                if min_width > 0 and min_height > 0:
                    meets_req, width, height, match_code = check_image_resolution(
                        filepath, min_width, min_height)
                    if meets_req:
                        match_type = {
                            3: "exact match",
                            2: "similar aspect ratio",
                            1: "larger resolution"}
                        logging.debug(
                            f"Successfully downloaded {url} to {filepath} with resolution ({width}x{height}), {match_type.get(match_code, 'acceptable')} for target {min_width}x{min_height}")
                        return True
                    else:
                        logging.warning(
                            f"Downloaded image {filename} has insufficient resolution: {width}x{height}, expected at least {min_width}x{min_height}")
                        # Remove the file since it doesn't meet the minimum
                        # resolution requirements
                        try:
                            os.remove(filepath)
                            logging.info(
                                f"Removed {filename} due to insufficient resolution")
                        except Exception as e:
                            logging.error(f"Failed to remove {filename}: {e}")
                        return False
                else:
                    logging.debug(
                        f"Successfully downloaded {url} to {filepath}")
                    return True
            else:
                logging.debug(
                    f"Failed to download {url}: HTTP {response.status_code}")

        except requests.exceptions.Timeout:
            logging.debug(f"Timeout downloading {url}")
        except requests.exceptions.ConnectionError:
            logging.debug(f"Connection error downloading {url}")
        except Exception as e:
            logging.debug(f"Error downloading {url}: {e}")

        # Apply exponential backoff if this is not the last attempt
        if attempt < retries:
            wait_time = delay * (2 ** (attempt - 1))  # Exponential backoff
            logging.debug(f"Retrying in {wait_time} seconds")
            time.sleep(wait_time)

    logging.warning(f"Failed to download {url} after {retries} attempts")
    return False


def main(
    themes: list[str],
    resolution: str = None,
    sites: list[str] = None,
    max_downloads: int = None,
    output_dir: str = None,
    workers: int = None,
    timeout: int = None,
    dry_run: bool = False,
    **kwargs
):
    """
    Main function to orchestrate wallpaper scraping and downloading.
    Enhanced with comprehensive options and dry-run capability.
    
    Args:
        themes: List of themes to search for
        resolution: Target resolution (e.g., '5120x1440')
        sites: List of specific sites to scrape (defaults to all enabled)
        max_downloads: Maximum downloads per theme
        output_dir: Custom output directory
        workers: Number of parallel workers
        timeout: Request timeout in seconds
        dry_run: If True, show what would be downloaded without downloading
    """
    # Import enhanced utilities
    from src.utils import validate_resolution, safe_filename, log_execution_time
    
    # Validate and set defaults from config
    if not resolution:
        resolution = CONFIG.get("RESOLUTION", "5120x1440")
    if not sites:
        sites = CONFIG.get("SITES", [])
    if not max_downloads:
        max_downloads = CONFIG.get("MAX_ITEMS_PER_THEME", 10)
    if not workers:
        workers = CONFIG.get("MAX_WORKERS", 4)
    if not timeout:
        timeout = CONFIG.get("REQUEST_TIMEOUT", 30)
    
    # Validate resolution format
    try:
        min_width, min_height = validate_resolution(resolution)
    except Exception as e:
        logging.error(f"Invalid resolution: {e}")
        return
    
    # Validate themes
    if not themes or not isinstance(themes, list):
        logging.error("No themes provided. Please specify at least one theme.")
        return

    logging.info(f"Starting wallpaper scraper with resolution {resolution}")
    logging.info(f"Themes: {', '.join(themes)}")
    logging.info(f"Sites: {', '.join(sites)}")
    logging.info(f"Max downloads per theme: {max_downloads}")
    if dry_run:
        logging.info("DRY RUN MODE: No files will be downloaded")

    # Prepare folders
    if output_dir:
        output_folder = output_dir
    else:
        output_folder = CONFIG["OUTPUT_FOLDER"]
    
    if not dry_run:
        os.makedirs(output_folder, exist_ok=True)
        logging.info(f"Output directory: {output_folder}")

    temp_folder = CONFIG.get("TEMP_FOLDER", os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp"))
    if not dry_run:
        os.makedirs(temp_folder, exist_ok=True)

    # Prepare download settings
    retries = CONFIG["MAX_RETRIES"]
    delay = CONFIG["RETRY_DELAY"]
    headers = {"User-Agent": CONFIG["USER_AGENT"]}

    # Service mapping - add new services here
    service_classes = {
        "wallpaperswide.com": WallpapersWideService,
        "wallhaven.cc": WallhavenService,
        "wallpaperbat.com": WallpaperBatService
    }

    # Filter sites to only those that are available and requested
    available_sites = [site for site in sites if site in service_classes]
    if not available_sites:
        logging.error(f"No valid sites found in: {sites}")
        logging.info(f"Available sites: {list(service_classes.keys())}")
        return
    
    logging.info(f"Scraping from {len(available_sites)} sites: {', '.join(available_sites)}")

    # Collect wallpaper URLs from all configured services in parallel, with progress bars
    all_urls = []
    scrape_futures = []
    scrape_progress = {}
    scrape_bars = {}
    
    # Prepare progress bars for each site
    for site in available_sites:
        if site in service_classes:
            # Calculate total steps for each site based on their process:
            if site == 'wallpaperbat.com':
                # For each theme:
                # 1. Start theme
                # 2. Process theme search
                # 3. Start ultrawide search (for 5120x1440)
                # 4. Process ultrawide results (for 5120x1440)
                # 5. Theme completion
                steps_per_theme = 3  # base steps
                if resolution == '5120x1440':
                    steps_per_theme += 2  # extra steps for ultrawide search
                total_steps = len(themes) * steps_per_theme
            elif site == 'wallpaperswide.com':
                # For each theme:
                # 1. Start theme
                # 2. Try first URL variant
                # 3. Try second URL variant (if needed)
                # 4. Theme completion
                total_steps = len(themes) * 4
            else:  # wallhaven.cc and others
                # For each theme:
                # 1. Start theme search
                # 2. Process results
                # 3. Theme completion
                total_steps = len(themes) * 3
            
            scrape_bars[site] = tqdm(
                total=total_steps, 
                desc=f"Scraping {site}", 
                position=len(scrape_bars), 
                **PROGRESS_BAR_CONFIG
            )
            scrape_progress[site] = 0
    def make_progress_callback(site):
        def progress_cb():
            scrape_bars[site].update(1)
        return progress_cb
    with ThreadPoolExecutor(max_workers=workers) as scrape_executor:
        for site in available_sites:
            if site in service_classes:
                logging.info(f"Submitting scrape for site: {site}")
                service_class = service_classes[site]
                service = service_class(
                    resolution=resolution,
                    themes=themes
                )
                # Pass a progress callback to the service
                scrape_futures.append(
                    scrape_executor.submit(
                        lambda svc=service, s=site: (s, svc.fetch_wallpapers(progress_callback=make_progress_callback(s)))
                    )
                )
            else:
                logging.warning(f"No service implemented for site: {site}")
        for future in as_completed(scrape_futures):
            try:
                site, site_urls = future.result()
                logging.info(f"Found {len(site_urls)} wallpapers from {site}")
                all_urls.extend(site_urls)
            except Exception as e:
                logging.error(f"Error processing site in parallel: {e}")
    # Close all progress bars
    for bar in scrape_bars.values():
        bar.close()

    # Remove duplicate URLs while preserving order
    unique_urls = []
    seen = set()
    for url in all_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)

    logging.info(f"Found {len(all_urls)} total wallpapers, {len(unique_urls)} unique")
    
    # Limit URLs per theme if max_downloads is specified
    if max_downloads and len(unique_urls) > max_downloads * len(themes):
        limited_urls = unique_urls[:max_downloads * len(themes)]
        logging.info(f"Limiting to {len(limited_urls)} wallpapers ({max_downloads} per theme)")
        unique_urls = limited_urls

    # Skip download if no wallpapers found
    if not unique_urls:
        logging.warning(
            "No wallpapers found. Check your configuration or network connection.")
        return

    # Dry run mode: just show what would be downloaded
    if dry_run:
        logging.info(f"DRY RUN: Would download {len(unique_urls)} wallpapers:")
        for i, url in enumerate(unique_urls[:10], 1):  # Show first 10
            logging.info(f"  {i}. {url}")
        if len(unique_urls) > 10:
            logging.info(f"  ... and {len(unique_urls) - 10} more")
        return

    # Parse the desired resolution
    try:
        min_width, min_height = map(
            int, resolution.lower().split("x"))
    except Exception as e:
        logging.error(
            f"Failed to parse resolution '{resolution}': {e}")
        min_width = min_height = 0

    # Filter out wallpapers that already exist with the correct resolution
    urls_to_download = []
    already_downloaded = 0
    for url in unique_urls:
        # Extract filename from URL and sanitize it
        filename = os.path.basename(url)
        filename = filename.replace("?", "_").replace("&", "_")
        filepath = os.path.join(output_folder, filename)

        if os.path.exists(filepath):
            # Check if the existing file has the correct resolution
            meets_req, width, height, match_code = check_image_resolution(
                filepath, min_width, min_height)
            if meets_req:
                already_downloaded += 1
                match_type = {
                    3: "exact match",
                    2: "similar aspect ratio",
                    1: "larger resolution"}
                logging.debug(
                    f"Skipping {filename} as it already exists with resolution ({width}x{height}), {match_type.get(match_code, 'acceptable')} for target {min_width}x{min_height}")
            else:
                logging.warning(
                    f"File {filename} exists but has insufficient resolution ({width}x{height}), will re-download")
                urls_to_download.append(url)
        else:
            urls_to_download.append(url)

    if already_downloaded > 0:
        logging.info(
            f"Skipping {already_downloaded} wallpapers that have already been downloaded")

    if not urls_to_download:
        logging.info(
            "No new wallpapers to download. All wallpapers already exist.")
        return

    # Download images using thread pool for parallelism
    logging.info(
        f"Downloading {len(urls_to_download)} new wallpapers with {workers} parallel workers")
    
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for url in urls_to_download:
            futures.append(
                executor.submit(
                    download_image,
                    url,
                    output_folder,
                    timeout,
                    retries,
                    delay,
                    headers,
                    min_width,
                    min_height))

        successes = 0
        for f in tqdm(
                as_completed(futures),
                total=len(futures),
                desc="Downloading"):
            if f.result():
                successes += 1

    # Summary of results
    total_downloaded = successes + already_downloaded
    total_wallpapers = len(unique_urls)
    success_rate = (successes / len(urls_to_download)) * \
        100 if urls_to_download else 100
    overall_success_rate = (
        total_downloaded / total_wallpapers) * 100 if total_wallpapers else 0

    logging.info(
        f"Downloaded {successes}/{len(urls_to_download)} new images ({success_rate:.1f}%)")
    logging.info(
        f"Total: {total_downloaded}/{total_wallpapers} images ({overall_success_rate:.1f}%) available in {output_folder}")


if __name__ == "__main__":
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--theme', type=str, required=True, help='Theme for wallpaper search (comma-separated for multiple)')
    parser.add_argument('--log-level', type=str, default=None)
    args = parser.parse_args()
    themes = [t.strip() for t in args.theme.split(',') if t.strip()]
    main(log_level=args.log_level, themes=themes)
