import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from tqdm import tqdm
import logging
import time
import sys
from PIL import Image  # For checking image dimensions

from config import CONFIG
from services.wallpaperswide_service import WallpapersWideService
from services.wallhaven_service import WallhavenService
from services.wallpaperbat_service import WallpaperBatService


def evaluate_resolution_match(width, height, target_width, target_height):
    """
    Evaluates how well an image matches desired resolution with fallback priorities.
    
    Args:
        width: Actual width of the image
        height: Actual height of the image
        target_width: Desired width
        target_height: Desired height
        
    Returns:
        Integer indicating the match quality:
        3: Exact match (perfect)
        2: Greater resolution with similar aspect ratio (good)
        1: Greater resolution with any aspect ratio (acceptable)
        0: Smaller resolution (unacceptable)
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
    Check if an image meets the minimum resolution requirements.
    
    Args:
        filepath: Path to the image file
        min_width: Minimum required width in pixels
        min_height: Minimum required height in pixels
        
    Returns:
        Tuple of (meets_requirement, actual_width, actual_height, match_code)
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
            match_code = evaluate_resolution_match(width, height, min_width, min_height)
            
            # Return whether it meets any of our acceptance criteria
            meets_requirement = match_code > 0
            return (meets_requirement, width, height, match_code)
    except Exception as e:
        logging.error(f"Error checking image resolution for {filepath}: {e}")
        return (False, 0, 0, 0)


def download_image(url, output_folder, timeout, retries, delay, headers, min_width=0, min_height=0):
    """
    Download a single image with retry logic and exponential backoff.
    
    Args:
        url: URL of the image to download
        output_folder: Folder to save the image
        timeout: Request timeout in seconds
        retries: Number of retry attempts
        delay: Base delay between retries (will be multiplied by attempt number)
        headers: HTTP headers to use for the request
        min_width: Minimum required width in pixels
        min_height: Minimum required height in pixels
        
    Returns:
        True if download was successful or file already exists with correct resolution, False otherwise
    """
    # Extract filename from URL and sanitize it
    filename = os.path.basename(url)
    # Replace any potentially problematic characters
    filename = filename.replace("?", "_").replace("&", "_")
    
    filepath = os.path.join(output_folder, filename)
    
    # Check if file already exists and has the correct resolution
    if os.path.exists(filepath):
        if min_width > 0 and min_height > 0:
            meets_req, width, height, match_code = check_image_resolution(filepath, min_width, min_height)
            if meets_req:
                match_type = {3: "exact match", 2: "similar aspect ratio", 1: "larger resolution"}
                logging.info(f"Skipping download of {filename} as it already exists with resolution ({width}x{height}), {match_type.get(match_code, 'acceptable')} for target {min_width}x{min_height}")
                return True
            else:
                logging.warning(f"File {filename} exists but has insufficient resolution ({width}x{height}), re-downloading")
                # Continue with download to replace the file
        else:
            logging.info(f"Skipping download of {filename} as it already exists (resolution not checked)")
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
                    meets_req, width, height, match_code = check_image_resolution(filepath, min_width, min_height)
                    if meets_req:
                        match_type = {3: "exact match", 2: "similar aspect ratio", 1: "larger resolution"}
                        logging.debug(f"Successfully downloaded {url} to {filepath} with resolution ({width}x{height}), {match_type.get(match_code, 'acceptable')} for target {min_width}x{min_height}")
                        return True
                    else:
                        logging.warning(f"Downloaded image {filename} has insufficient resolution: {width}x{height}, expected at least {min_width}x{min_height}")
                        # Remove the file since it doesn't meet the minimum resolution requirements
                        try:
                            os.remove(filepath)
                            logging.info(f"Removed {filename} due to insufficient resolution")
                        except Exception as e:
                            logging.error(f"Failed to remove {filename}: {e}")
                        return False
                else:
                    logging.debug(f"Successfully downloaded {url} to {filepath}")
                    return True
            else:
                logging.debug(f"Failed to download {url}: HTTP {response.status_code}")
                
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


def main():
    """Main function to orchestrate wallpaper scraping and downloading."""
    # Configure logging to console and file
    log_level = CONFIG.get("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Set up a formatter that includes timestamp, level, and message
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    
    # Configure logging to both console and file
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),  # Log to console
            logging.FileHandler(os.path.join(CONFIG.get("TEMP_FOLDER", "."), "wallpaper_scraper.log"))  # Log to file
        ]
    )

    logging.info(f"Starting wallpaper scraper with resolution {CONFIG['RESOLUTION']}")
    logging.info(f"Themes: {', '.join(CONFIG['THEMES'])}")
    logging.info(f"Sites: {', '.join(CONFIG['SITES'])}")

    # Prepare folders
    output_folder = CONFIG["OUTPUT_FOLDER"]
    os.makedirs(output_folder, exist_ok=True)
    
    if "TEMP_FOLDER" in CONFIG:
        os.makedirs(CONFIG["TEMP_FOLDER"], exist_ok=True)

    # Prepare download settings
    timeout = CONFIG["REQUEST_TIMEOUT"]
    retries = CONFIG["MAX_RETRIES"]
    delay = CONFIG["RETRY_DELAY"]
    headers = {"User-Agent": CONFIG["USER_AGENT"]}
    max_workers = CONFIG["MAX_WORKERS"]
    
    # Service mapping - add new services here
    service_classes = {
        "wallpaperswide.com": WallpapersWideService,
        "wallhaven.cc": WallhavenService,
        "wallpaperbat.com": WallpaperBatService
    }

    # Collect wallpaper URLs from all configured services
    all_urls = []
    
    # Process each site
    for site in CONFIG["SITES"]:
        if site in service_classes:
            logging.info(f"Processing site: {site}")
            
            try:
                # Instantiate the appropriate service
                service_class = service_classes[site]
                service = service_class(
                    resolution=CONFIG["RESOLUTION"],
                    themes=CONFIG["THEMES"]
                )
                
                # Fetch wallpapers from this service
                site_urls = service.fetch_wallpapers()
                logging.info(f"Found {len(site_urls)} wallpapers from {site}")
                
                all_urls.extend(site_urls)
            except Exception as e:
                logging.error(f"Error processing site {site}: {e}")
        else:
            logging.warning(f"No service implemented for site: {site}")
    
    # Remove duplicate URLs while preserving order
    unique_urls = []
    seen = set()
    for url in all_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    logging.info(f"Found {len(unique_urls)} unique wallpapers to download")
    
    # Skip download if no wallpapers found
    if not unique_urls:
        logging.warning("No wallpapers found. Check your configuration or network connection.")
        return
    
    # Parse the desired resolution
    try:
        min_width, min_height = map(int, CONFIG["RESOLUTION"].lower().split("x"))
    except Exception as e:
        logging.error(f"Failed to parse resolution '{CONFIG['RESOLUTION']}': {e}")
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
            meets_req, width, height, match_code = check_image_resolution(filepath, min_width, min_height)
            if meets_req:
                already_downloaded += 1
                match_type = {3: "exact match", 2: "similar aspect ratio", 1: "larger resolution"}
                logging.debug(f"Skipping {filename} as it already exists with resolution ({width}x{height}), {match_type.get(match_code, 'acceptable')} for target {min_width}x{min_height}")
            else:
                logging.warning(f"File {filename} exists but has insufficient resolution ({width}x{height}), will re-download")
                urls_to_download.append(url)
        else:
            urls_to_download.append(url)
    
    if already_downloaded > 0:
        logging.info(f"Skipping {already_downloaded} wallpapers that have already been downloaded")
    
    if not urls_to_download:
        logging.info("No new wallpapers to download. All wallpapers already exist.")
        return
    
    # Download images using thread pool for parallelism
    logging.info(f"Downloading {len(urls_to_download)} new wallpapers with {max_workers} parallel workers")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for url in urls_to_download:
            futures.append(executor.submit(
                download_image, url, output_folder, timeout, retries, delay, headers, min_width, min_height
            ))

        successes = 0
        for f in tqdm(as_completed(futures), total=len(futures), desc="Downloading"):
            if f.result():
                successes += 1

    # Summary of results
    total_downloaded = successes + already_downloaded
    total_wallpapers = len(unique_urls)
    success_rate = (successes / len(urls_to_download)) * 100 if urls_to_download else 100
    overall_success_rate = (total_downloaded / total_wallpapers) * 100 if total_wallpapers else 0
    
    logging.info(f"Downloaded {successes}/{len(urls_to_download)} new images ({success_rate:.1f}%)")
    logging.info(f"Total: {total_downloaded}/{total_wallpapers} images ({overall_success_rate:.1f}%) available in {output_folder}")


if __name__ == "__main__":
    main()