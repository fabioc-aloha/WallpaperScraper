"""
Service module for fetching wallpapers from wallpaperbat.com.
"""
import requests
from bs4 import BeautifulSoup
import re
import logging
from urllib.parse import urljoin, quote_plus
import time
from config import CONFIG, DEFAULT_HEADERS

class WallpaperBatService:
    """
    Service for fetching wallpapers from wallpaperbat.com which has a collection
    of super ultrawide wallpapers and various other resolutions.
    """
    BASE_URL = "https://wallpaperbat.com"
    
    def __init__(self, resolution="5120x1440", themes=None):
        """
        Initialize the service with the desired resolution and themes.
        
        Args:
            resolution: String with the desired wallpaper resolution (e.g., '5120x1440')
            themes: List of themes to search for (e.g., ['nature', 'abstract'])
        """
        self.resolution = resolution.lower()
        self.themes = themes or []
        
        # Parse resolution for comparison purposes
        try:
            self.min_width, self.min_height = map(int, resolution.lower().split('x'))
        except Exception as e:
            logging.error(f"Failed to parse resolution '{resolution}': {e}")
            self.min_width = self.min_height = 0
              # Set up headers using centralized configuration
        self.headers = DEFAULT_HEADERS.copy()
        self.headers['User-Agent'] = CONFIG['USER_AGENT']
    def fetch_wallpapers(self, progress_callback=None):
        """
        Fetch wallpaper download URLs by theme and resolution.
        
        Args:
            progress_callback: Optional callback function to report progress
            
        Returns:
            List of wallpaper download URLs matching the requested criteria.
        """
        wallpapers = []
        
        # Wallpaperbat has specific URL format for super ultrawide resolution
        resolution_url = f"{self.BASE_URL}/{self.resolution}-super-ultrawide-wallpapers"
        
        # Process each theme
        for theme in self.themes:
            theme_wallpapers = []
            
            # Progress: Starting theme search
            if progress_callback:
                progress_callback()
            
            # Try theme-specific page with resolution
            theme_search = quote_plus(theme)
            search_url = f"{self.BASE_URL}/search?q={theme_search}"
            
            # Progress: Processing theme search results
            if progress_callback:
                progress_callback()
                
            theme_wallpapers.extend(self._process_search_page(search_url))
            
            # If we're looking for a specific resolution that has its own page, check that too
            if self.resolution == "5120x1440":
                # Progress: Starting ultrawide search
                if progress_callback:
                    progress_callback()
                    
                ultrawide_url = f"{self.BASE_URL}/5120x1440-super-ultrawide-wallpapers"
                ultrawide_wallpapers = self._process_search_page(ultrawide_url)
                
                # Progress: Processing ultrawide results
                if progress_callback:
                    progress_callback()
                
                # If this is a theme search, filter the ultrawide results to only include ones matching the theme
                if theme.lower() not in ['ultrawide', 'super ultrawide', 'wide', '5120x1440']:
                    # Keep only wallpapers that might match our theme (simple text matching)
                    filtered_wallpapers = []
                    for url in ultrawide_wallpapers:
                        # Extract keywords from the URL and check if they match our theme
                        if theme.lower() in url.lower():
                            filtered_wallpapers.append(url)
                    theme_wallpapers.extend(filtered_wallpapers)
                else:
                    # If we're specifically looking for ultrawide wallpapers, keep all results
                    theme_wallpapers.extend(ultrawide_wallpapers)
                    
            wallpapers.extend(theme_wallpapers)
            logging.info(f"Found {len(theme_wallpapers)} wallpapers for theme '{theme}' on wallpaperbat.com")
            
            # Progress: Theme completed
            if progress_callback:
                progress_callback()
            
            # Add delay between theme requests
            time.sleep(CONFIG.get('REQUEST_DELAY', 2.0))
        
        # Remove duplicates while preserving order
        unique_wallpapers = []
        seen = set()
        for url in wallpapers:
            if url not in seen:
                seen.add(url)
                unique_wallpapers.append(url)
        
        logging.info(f"Found {len(unique_wallpapers)} unique wallpapers from wallpaperbat.com")
        return unique_wallpapers
    
    def _process_search_page(self, url, progress_callback=None):
        """
        Process a search results page to find wallpaper detail pages.
        
        Args:
            url: The URL of the search results page
            progress_callback: Optional callback function to report progress
            
        Returns:
            List of wallpaper download URLs
        """
        wallpapers = []
        
        try:
            response = self._fetch_with_retry(url)
            if response is None:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for wallpaper cards/items that contain images
            wallpaper_items = soup.select('div.wallpapers a')
            if not wallpaper_items:
                # Try alternative selectors
                wallpaper_items = soup.select('div.item a')
            if not wallpaper_items:
                # Try another approach - look for images inside links
                wallpaper_items = [a for a in soup.select('a') if a.find('img')]
                
            logging.debug(f"Found {len(wallpaper_items)} wallpaper items on page: {url}")
            
            # Process each wallpaper item up to the maximum per theme
            max_items = CONFIG.get('MAX_ITEMS_PER_THEME', 10)
            for i, item in enumerate(wallpaper_items):
                if i >= max_items:
                    break
                    
                try:
                    # Get the detail page URL
                    if not item.has_attr('href'):
                        continue
                        
                    detail_url = item['href']
                    if not detail_url.startswith(('http://', 'https://')):
                        detail_url = urljoin(self.BASE_URL, detail_url)
                    
                    logging.debug(f"Processing wallpaper detail page: {detail_url}")
                    
                    # Get download links from the detail page
                    download_urls = self._process_detail_page(detail_url)
                    wallpapers.extend(download_urls)
                    
                    # Update progress after each wallpaper
                    if progress_callback:
                        progress_callback()
                    
                    # Add a short delay between requests
                    time.sleep(CONFIG.get('REQUEST_DELAY', 2.0))
                    
                except Exception as e:
                    logging.error(f"Error processing wallpaper item: {e}")
            
        except Exception as e:
            logging.error(f"Error processing search page {url}: {e}")
        
        return wallpapers
    
    def _process_detail_page(self, url):
        """
        Process a wallpaper detail page to find download links.
        
        Args:
            url: The URL of the detail page
            
        Returns:
            List of wallpaper download URLs with matching resolution
        """
        download_links = []
        
        try:
            response = self._fetch_with_retry(url)
            if response is None:
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the high-resolution image and download options
            wallpaper_options = []
            
            # Try to find the main image first
            main_img = soup.select_one('img.img-wallpaper')
            if not main_img:
                main_img = soup.select_one('img#wallpaper')
            if not main_img:
                # Try alternative approach - find the largest image on the page
                all_imgs = soup.select('img')
                if all_imgs:
                    # Find images with src attribute
                    imgs_with_src = [img for img in all_imgs if img.has_attr('src')]
                    if imgs_with_src:
                        # Sort by assumed size (length of src URL often correlates with image size)
                        imgs_with_src.sort(key=lambda x: len(x['src']), reverse=True)
                        main_img = imgs_with_src[0]
            
            if main_img and main_img.has_attr('src'):
                img_url = main_img['src']
                
                # Check if the URL is relative or absolute
                if not img_url.startswith(('http://', 'https://')):
                    img_url = urljoin(self.BASE_URL, img_url)
                
                # Try to determine resolution from image attributes or URL
                width = main_img.get('width') or main_img.get('data-width')
                height = main_img.get('height') or main_img.get('data-height')
                
                # If no width/height in attributes, try to find it in URL or nearby text
                if not (width and height):
                    # Try to extract resolution from URL
                    res_match = re.search(r'(\d+)x(\d+)', img_url)
                    if res_match:
                        width = res_match.group(1)
                        height = res_match.group(2)
                        
                # If we found width and height, use them
                if width and height:
                    try:
                        width = int(width)
                        height = int(height)
                        
                        # Add to options with resolution details
                        wallpaper_options.append({
                            'url': img_url,
                            'width': width,
                            'height': height,
                            'exact_match': width == self.min_width and height == self.min_height
                        })
                        logging.debug(f"Found download option: {img_url} ({width}x{height})")
                    except (ValueError, TypeError) as e:
                        # If we can't parse the resolution, still add the URL
                        logging.warning(f"Couldn't parse resolution for {img_url}: {e}")
                        wallpaper_options.append({
                            'url': img_url,
                            'width': self.min_width,  # Assume it matches what we searched for
                            'height': self.min_height,
                            'exact_match': False
                        })
                else:
                    # No resolution info available, assume it matches our search
                    wallpaper_options.append({
                        'url': img_url,
                        'width': self.min_width,
                        'height': self.min_height,
                        'exact_match': False
                    })
                    logging.debug(f"Found download without resolution info: {img_url}")
                    
            # Also look for download links or buttons that might contain high-res images
            download_buttons = soup.select('a.download-button, a.btn-download')
            for button in download_buttons:
                if button.has_attr('href'):
                    dl_url = button['href']
                    if not dl_url.startswith(('http://', 'https://')):
                        dl_url = urljoin(self.BASE_URL, dl_url)
                    
                    # Try to extract resolution from the link text or URL
                    res_match = None
                    if button.get_text():
                        res_match = re.search(r'(\d+)\s*[xX]\s*(\d+)', button.get_text())
                    if not res_match:
                        res_match = re.search(r'(\d+)x(\d+)', dl_url)
                        
                    if res_match:
                        try:
                            width = int(res_match.group(1))
                            height = int(res_match.group(2))
                            
                            wallpaper_options.append({
                                'url': dl_url,
                                'width': width,
                                'height': height,
                                'exact_match': width == self.min_width and height == self.min_height
                            })
                            logging.debug(f"Found download button: {dl_url} ({width}x{height})")
                        except (ValueError, TypeError) as e:
                            logging.warning(f"Couldn't parse resolution in button: {e}")
                    else:
                        # Add without resolution info
                        wallpaper_options.append({
                            'url': dl_url,
                            'width': self.min_width,  # Assume it matches
                            'height': self.min_height,
                            'exact_match': False
                        })
            
            # Process the resolution selection logic
            if wallpaper_options:
                # First, check for exact matches
                exact_matches = [opt for opt in wallpaper_options if opt['exact_match']]
                if exact_matches:
                    # Use the first exact match
                    chosen = exact_matches[0]
                    download_links.append(chosen['url'])
                    logging.info(f"Found exact resolution match: {chosen['url']} ({chosen['width']}x{chosen['height']})")
                else:
                    # No exact match, find the smallest one that's bigger than our minimum
                    valid_options = [opt for opt in wallpaper_options 
                                    if opt['width'] >= self.min_width and opt['height'] >= self.min_height]
                    
                    if valid_options:
                        # Sort by resolution area to find the closest one
                        valid_options.sort(key=lambda x: x['width'] * x['height'])
                        chosen = valid_options[0]  # Smallest valid resolution
                        download_links.append(chosen['url'])
                        logging.info(f"Found next larger resolution: {chosen['url']} ({chosen['width']}x{chosen['height']})")
                    else:
                        # If nothing is bigger than what we want, just use the largest available
                        wallpaper_options.sort(key=lambda x: x['width'] * x['height'], reverse=True)
                        chosen = wallpaper_options[0]  # Largest resolution
                        download_links.append(chosen['url'])
                        logging.info(f"Using largest available resolution: {chosen['url']} ({chosen['width']}x{chosen['height']})")
            
        except Exception as e:
            logging.error(f"Error processing detail page {url}: {e}")
            
        return download_links
    
    def _fetch_with_retry(self, url):
        """
        Fetch a URL with retry logic and exponential backoff.
        
        Args:
            url: The URL to fetch
            
        Returns:
            Response object if successful, None otherwise
        """
        timeout = CONFIG.get('REQUEST_TIMEOUT', 10)
        max_retries = CONFIG.get('MAX_RETRIES', 3)
        retry_delay = CONFIG.get('RETRY_DELAY', 1)
        
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=timeout)
                
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Too Many Requests
                    # Special handling for rate limiting
                    logging.warning(f"Rate limited by wallpaperbat.com on attempt {attempt + 1}")
                    wait_time = retry_delay * (2 ** attempt) + 2  # Add extra time for rate limiting
                else:
                    logging.warning(f"HTTP {response.status_code} fetching {url} on attempt {attempt + 1}")
            except (requests.exceptions.RequestException, IOError) as e:
                logging.warning(f"Error fetching {url} on attempt {attempt + 1}: {e}")
                
            # Apply exponential backoff if this is not the last attempt
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logging.debug(f"Retrying in {wait_time} seconds")
                time.sleep(wait_time)
                
        logging.error(f"Failed to fetch {url} after {max_retries} attempts")
        return None
