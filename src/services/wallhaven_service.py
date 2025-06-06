"""
Service module for fetching wallpapers from wallhaven.cc.
"""
import requests
from bs4 import BeautifulSoup
import re
import logging
from urllib.parse import urljoin, quote_plus
import time
from config import CONFIG, DEFAULT_HEADERS

class WallhavenService:
    """
    Service for fetching wallpapers from wallhaven.cc which has a wide variety
    of high-resolution wallpapers and supports search by resolution.
    """
    BASE_URL = "https://wallhaven.cc"
    
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
        
        # Process each theme
        for theme in self.themes:
            # Progress: Starting theme search
            if progress_callback:
                progress_callback()
                
            theme_wallpapers = self._fetch_theme_wallpapers(theme)
            wallpapers.extend(theme_wallpapers)
            logging.info(f"Found {len(theme_wallpapers)} wallpapers for theme '{theme}'")
            
            # Progress: Processing search results
            if progress_callback:
                progress_callback()
            
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
        
        logging.info(f"Found {len(unique_wallpapers)} unique wallpapers from wallhaven.cc")
        return unique_wallpapers
    
    def _fetch_theme_wallpapers(self, theme, progress_callback=None):
        """
        Fetch wallpapers for a specific theme.
        
        Args:
            theme: The theme to search for
            progress_callback: Optional callback function to report progress
            
        Returns:
            List of wallpaper URLs
        """
        wallpapers = []
        
        # Build the search URL for this theme and resolution
        search_term = quote_plus(theme)
        resolutions = f"{self.min_width}x{self.min_height}"
        search_url = f"{self.BASE_URL}/search?q={search_term}&resolutions={resolutions}"
        
        logging.info(f"Searching wallhaven.cc for '{theme}' with resolution {resolutions}: {search_url}")
        
        try:
            response = self._fetch_with_retry(search_url)
            if response is None:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for wallpaper preview images
            wallpaper_items = soup.select('figure.thumb')
            logging.debug(f"Found {len(wallpaper_items)} wallpaper items")
            
            # Process each wallpaper up to the maximum per theme
            max_items = CONFIG.get('MAX_ITEMS_PER_THEME', 10)
            for item in wallpaper_items[:max_items]:
                try:
                    # Extract wallpaper info
                    link = item.select_one('a.preview')
                    if not link or not link.has_attr('href'):
                        continue
                    
                    detail_url = link['href']
                    if not detail_url.startswith(('http://', 'https://')):
                        detail_url = urljoin(self.BASE_URL, detail_url)
                    
                    # Get the actual wallpaper URLs from the detail page
                    download_urls = self._process_detail_page(detail_url)
                    wallpapers.extend(download_urls)
                    
                    # Update progress after each wallpaper
                    if progress_callback:
                        progress_callback()
                    
                except Exception as e:
                    logging.error(f"Error processing wallpaper item: {e}")
                    continue
                    
                # Add delay between wallpaper requests
                time.sleep(CONFIG.get('REQUEST_DELAY', 1))
                
        except Exception as e:
            logging.error(f"Error fetching theme {theme}: {e}")
            
        return wallpapers
    
    def _process_detail_page(self, url):
        """
        Process a wallpaper detail page to find the download link.
        
        Args:
            url: The URL of the detail page
            
        Returns:
            List containing the wallpaper download URL if found, empty list otherwise
        """
        download_urls = []
        
        try:
            response = self._fetch_with_retry(url)
            if response is None:
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the main wallpaper image or download link
            wallpaper_options = []
            
            # Try to find the high-resolution download button/link
            download_link = soup.select_one('img#wallpaper')
            if download_link and download_link.has_attr('src'):
                img_url = download_link['src']
                
                # Check if the URL is relative or absolute
                if not img_url.startswith(('http://', 'https://')):
                    img_url = urljoin(self.BASE_URL, img_url)
                
                # Try to get resolution from URL or attributes
                width = download_link.get('data-wallpaper-width') or download_link.get('width')
                height = download_link.get('data-wallpaper-height') or download_link.get('height')
                
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
            
            # Process the resolution selection logic
            if wallpaper_options:
                # First, check for exact match
                exact_matches = [opt for opt in wallpaper_options if opt['exact_match']]
                if exact_matches:
                    # Exactly one match with our desired resolution, use it
                    chosen = exact_matches[0]
                    download_urls.append(chosen['url'])
                    logging.info(f"Found exact resolution match: {chosen['url']} ({chosen['width']}x{chosen['height']})")
                else:
                    # No exact match, find the smallest one that's bigger than our minimum
                    valid_options = [opt for opt in wallpaper_options 
                                    if opt['width'] >= self.min_width and opt['height'] >= self.min_height]
                    
                    if valid_options:
                        # Sort by resolution area (width * height) to find the closest one
                        valid_options.sort(key=lambda x: x['width'] * x['height'])
                        chosen = valid_options[0]  # Smallest valid resolution
                        download_urls.append(chosen['url'])
                        logging.info(f"Found next larger resolution: {chosen['url']} ({chosen['width']}x{chosen['height']})")
                    else:
                        logging.debug(f"No suitable resolution found that meets {self.min_width}x{self.min_height}")
            
        except Exception as e:
            logging.error(f"Error processing detail page {url}: {e}")
            
        return download_urls
    
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
                    logging.warning(f"Rate limited by wallhaven.cc on attempt {attempt + 1}")
                    wait_time = retry_delay * (2 ** attempt) + 2  # Add extra time for rate limiting
                else:
                    logging.warning(f"HTTP {response.status_code} fetching {url} on attempt {attempt + 1}")
            except Exception as e:
                logging.warning(f"Error fetching {url} on attempt {attempt + 1}: {e}")
                
            # Apply exponential backoff if this is not the last attempt
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logging.debug(f"Retrying in {wait_time} seconds")
                time.sleep(wait_time)
                
        logging.error(f"Failed to fetch {url} after {max_retries} attempts")
        return None
