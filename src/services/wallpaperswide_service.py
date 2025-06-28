"""
Service module for fetching wallpapers from wallpaperswide.com.
"""
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import logging
from src.config import CONFIG, DEFAULT_HEADERS
import time

class WallpapersWideService:
    """
    Service for fetching wallpapers from wallpaperswide.com which has a different
    structure than other wallpaper sites and supports direct resolution filtering.
    """
    BASE_URL = "https://wallpaperswide.com"

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
            self.min_width = self.min_height = 0        # Set up headers using centralized configuration
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

        # This site allows direct resolution filtering via URL
        resolution_url = f"{self.resolution}-wallpapers-r.html"
        
        # Process each theme
        for theme in self.themes:
            # Progress: Starting theme
            if progress_callback:
                progress_callback()
                
            theme_urls = []
            
            # Try theme-specific page first
            theme_path = f"{theme}-desktop-wallpapers.html"
            theme_url = urljoin(self.BASE_URL, theme_path)
            theme_urls.append(theme_url)
            
            # Also try resolution-specific URL with theme
            # Some sites have URLs like /5120x1440-nature-wallpapers-r.html
            alt_theme_path = f"{self.resolution}-{theme}-wallpapers-r.html"
            alt_theme_url = urljoin(self.BASE_URL, alt_theme_path)
            theme_urls.append(alt_theme_url)
            
            # Process each URL approach
            for url in theme_urls:
                # Progress: Trying URL variant
                if progress_callback:
                    progress_callback()
                    
                logging.info(f"Fetching theme page: {url}")
                try:
                    theme_wallpapers = self._process_theme_page(url)
                    wallpapers.extend(theme_wallpapers)
                    
                    if theme_wallpapers:
                        logging.info(f"Found {len(theme_wallpapers)} wallpapers for {theme} using {url}")
                        break  # If we found wallpapers, no need to try alternative URL
                except Exception as e:
                    logging.error(f"Error processing theme page {url}: {e}")
                
                # Delay to avoid overloading the server
                time.sleep(CONFIG.get('REQUEST_DELAY', 1))
            
            # Progress: Theme completed
            if progress_callback:
                progress_callback()
        
        # Remove duplicates while preserving order
        unique_wallpapers = []
        seen = set()
        for url in wallpapers:
            if url not in seen:
                seen.add(url)
                unique_wallpapers.append(url)
        
        logging.info(f"Found {len(unique_wallpapers)} unique wallpapers from wallpaperswide.com")
        return unique_wallpapers
    
    def _process_theme_page(self, url, progress_callback=None):
        """
        Process a theme page to find wallpaper detail pages.
        
        Args:
            url: The URL of the theme page
            progress_callback: Optional callback function to report progress
            
        Returns:
            List of wallpaper download URLs
        """
        wallpapers = []
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Try different selectors to find wallpaper containers
                wallpaper_items = soup.select('div.wallpaper')  # Primary selector
                if not wallpaper_items:
                    # Try alternative selectors
                    wallpaper_items = soup.select('div.item')
                    if not wallpaper_items:
                        wallpaper_items = soup.select('a.wallpapers-image')
                
                # Process each wallpaper up to the maximum
                max_items = CONFIG.get('MAX_ITEMS_PER_THEME', 10)
                for i, item in enumerate(wallpaper_items[:max_items]):
                    try:
                        # Get the detail page URL
                        detail_url = None
                        link = item.find('a')
                        if link and link.has_attr('href'):
                            detail_url = link['href']
                        
                        if detail_url:
                            if not detail_url.startswith(('http://', 'https://')):
                                detail_url = urljoin(self.BASE_URL, detail_url)
                            
                            # Get download links from the detail page
                            download_urls = self._process_detail_page(detail_url)
                            wallpapers.extend(download_urls)
                            
                            # Update progress after each wallpaper
                            if progress_callback:
                                progress_callback()
                            
                            # Add delay between requests
                            time.sleep(CONFIG.get('REQUEST_DELAY', 1))
                            
                    except Exception as e:
                        logging.error(f"Error processing wallpaper item: {e}")
                        continue
                        
        except Exception as e:
            logging.error(f"Error processing theme page {url}: {e}")
            
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
        timeout = CONFIG.get('REQUEST_TIMEOUT', 10)
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=timeout)
            if resp.status_code != 200:
                logging.warning(f"Failed to fetch detail page {url}, status {resp.status_code}")
                return []
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Look for download links with resolution information
            # WallpapersWide typically has direct download links with resolution in the text
            all_links = soup.find_all('a', href=True)
            
            # Store all wallpaper options with their resolutions
            wallpaper_options = []
            
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text().strip()
                
                # Check for links containing "/download/" and our desired resolution
                if '/download/' in href and href.endswith(('.jpg', '.png', '.jpeg')):
                    resolution_match = re.search(r'(\d+)x(\d+)', href) or re.search(r'(\d+)\s*[xX]\s*(\d+)', text)
                    
                    if resolution_match:
                        try:
                            width = int(resolution_match.group(1))
                            height = int(resolution_match.group(2))
                            download_url = urljoin(self.BASE_URL, href)
                            
                            # Add to options list with resolution details
                            wallpaper_options.append({
                                'url': download_url,
                                'width': width,
                                'height': height,
                                'exact_match': width == self.min_width and height == self.min_height
                            })
                            logging.debug(f"Found download option: {download_url} ({width}x{height})")
                        except (ValueError, IndexError) as e:
                            logging.warning(f"Failed to parse resolution in '{text}' or '{href}': {e}")
            
            # Process the resolution selection logic
            if wallpaper_options:
                # First, check for exact match
                exact_matches = [opt for opt in wallpaper_options if opt['exact_match']]
                if exact_matches:
                    # Exactly one match with our desired resolution, use it
                    chosen = exact_matches[0]
                    download_links.append(chosen['url'])
                    logging.debug(f"Found exact resolution match: {chosen['url']} ({chosen['width']}x{chosen['height']})")
                else:
                    # No exact match, find the smallest one that's bigger than our minimum
                    valid_options = [opt for opt in wallpaper_options 
                                    if opt['width'] >= self.min_width and opt['height'] >= self.min_height]
                    
                    if valid_options:
                        # Sort by resolution area (width * height) to find the closest one
                        valid_options.sort(key=lambda x: x['width'] * x['height'])
                        chosen = valid_options[0]  # Smallest valid resolution
                        download_links.append(chosen['url'])
                        logging.debug(f"Found next larger resolution: {chosen['url']} ({chosen['width']}x{chosen['height']})")
                    else:
                        logging.debug(f"No suitable resolution found that meets {self.min_width}x{self.min_height}")
            
        except Exception as e:
            logging.error(f"Error processing detail page {url}: {e}")
        
        return download_links
