import requests
from bs4 import BeautifulSoup
from config import CONFIG
from urllib.parse import urljoin
import re
import logging
import time

class FourKWallpapersService:
    """
    Service for fetching wallpapers from 4kwallpapers.com.
    
    This service adapts to the current structure of 4kwallpapers.com, which
    has changed from the original implementation. It uses multiple fallback
    strategies to locate wallpapers.
    """

    BASE_URL = "https://4kwallpapers.com"

    def __init__(self, resolution="5120x1440", themes=None):
        """
        Initialize the service with the desired resolution and themes.
        
        Args:
            resolution: String with the desired wallpaper resolution (e.g., '5120x1440')
            themes: List of themes to search for (e.g., ['nature', 'abstract'])
        """
        self.resolution = resolution.lower()
        self.themes = themes or []
        
        # Minimum width and height thresholds
        try:
            self.min_width, self.min_height = map(int, resolution.lower().split('x'))
        except Exception as e:
            logging.error(f"Failed to parse resolution '{resolution}': {e}")
            self.min_width = self.min_height = 0
            
        # Set up comprehensive headers to avoid being detected as a bot
        self.headers = {
            'User-Agent': CONFIG['USER_AGENT'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def fetch_wallpapers(self):
        """
        Fetch wallpaper download URLs by theme and resolution using adaptive techniques.
        
        Returns:
            List of wallpaper download URLs matching the requested criteria.
        """
        wallpapers = []
        
        for theme in self.themes:
            # Fetch the category page for the theme
            search_url = urljoin(self.BASE_URL, f"/{theme}")
            logging.info(f"Fetching search page: {search_url}")
            
            try:
                resp = self._fetch_with_retry(search_url)
                if resp is None:
                    continue
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Try multiple strategies to find wallpaper detail pages
                wallpaper_links = []
                
                # Strategy 1: Look for image thumbnails with parent links
                logging.debug("Looking for image thumbnails with parent links")
                for img in soup.find_all('img'):
                    parent = img.find_parent('a')
                    if parent and parent.has_attr('href'):
                        href = parent['href']
                        # Only include links that look like wallpaper detail pages
                        if href.startswith(f'/{theme}/') and href.count('/') >= 2:
                            wallpaper_links.append(href)
                            logging.debug(f"Found thumbnail link: {href}")
                
                # Strategy 2: If no links found, try figure elements if present
                if not wallpaper_links:
                    logging.debug("Looking for figure elements")
                    all_figures = soup.find_all('figure')
                    for figure in all_figures:
                        a_tag = figure.find('a', href=True)
                        if a_tag:
                            wallpaper_links.append(a_tag['href'])
                            logging.debug(f"Found figure link: {a_tag['href']}")
                
                # Strategy 3: If still no links, look for any links with theme in the path
                if not wallpaper_links:
                    logging.debug("Looking for links containing theme path")
                    all_links = soup.find_all('a', href=True)
                    for link in all_links:
                        href = link['href']
                        if href.startswith(f'/{theme}/') and href not in wallpaper_links:
                            wallpaper_links.append(href)
                            logging.debug(f"Found theme link: {href}")
                
                logging.info(f"Found {len(wallpaper_links)} potential wallpaper pages for theme {theme}")
                
                # Process the detail pages
                for href in wallpaper_links[:CONFIG.get('MAX_ITEMS_PER_THEME', 10)]:
                    detail_url = urljoin(self.BASE_URL, href)
                    logging.info(f"Visiting detail page: {detail_url}")
                    
                    try:
                        detail_urls = self._process_detail_page(detail_url)
                        wallpapers.extend(detail_urls)
                    except Exception as e:
                        logging.error(f"Error processing detail page {detail_url}: {e}")
                    
                    # Add a delay to avoid overloading the server
                    time.sleep(CONFIG.get('REQUEST_DELAY', 1))
                    
            except Exception as e:
                logging.error(f"Error fetching theme page {search_url}: {e}")
        
        # Remove duplicates while preserving order
        unique_wallpapers = []
        seen = set()
        for url in wallpapers:
            if url not in seen:
                seen.add(url)
                unique_wallpapers.append(url)
        
        logging.info(f"Found {len(unique_wallpapers)} unique wallpapers from 4kwallpapers.com")
        return unique_wallpapers
    
    def _fetch_with_retry(self, url):
        """
        Fetch a URL with retry logic and exponential backoff.
        
        Args:
            url: URL to fetch
            
        Returns:
            Requests response object or None if all retries failed
        """
        timeout = CONFIG.get('REQUEST_TIMEOUT', 10)
        max_retries = CONFIG.get('MAX_RETRIES', 3)
        retry_delay = CONFIG.get('RETRY_DELAY', 1)
        
        for attempt in range(max_retries):
            try:
                resp = requests.get(url, headers=self.headers, timeout=timeout)
                
                if resp.status_code == 200:
                    return resp
                else:
                    logging.warning(f"Request to {url} returned status {resp.status_code}")
            except (requests.RequestException, IOError) as e:
                logging.warning(f"Request to {url} failed: {e}")
            
            # Apply exponential backoff
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logging.debug(f"Retrying in {wait_time} seconds")
                time.sleep(wait_time)
        
        logging.error(f"All {max_retries} requests to {url} failed")
        return None
    
    def _process_detail_page(self, url):
        """
        Process a wallpaper detail page to find download links.
        
        Args:
            url: URL of the detail page
            
        Returns:
            List of wallpaper download URLs with matching resolution
        """
        download_urls = []
        
        resp = self._fetch_with_retry(url)
        if resp is None:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Multiple strategies to find download links
        
        # Track all available resolutions to support our selection logic
        wallpaper_options = []
        
        # Strategy 1: Look for links with resolution in text
        logging.debug("Looking for links with resolution in text")
        for link in soup.find_all('a', href=True):
            text = link.get_text().strip()
            href = link.get('href', '')
            
            # Skip links that don't look like downloads
            if not (href.endswith('.jpg') or href.endswith('.png') or 'download' in href.lower()):
                continue
                
            # Check for resolution in the text
            resolution_match = re.search(r'(\d+)\s*[xX]\s*(\d+)', text)
            if resolution_match:
                try:
                    width = int(resolution_match.group(1))
                    height = int(resolution_match.group(2))
                    download_url = urljoin(self.BASE_URL, href)
                    
                    # Add to options with resolution details
                    wallpaper_options.append({
                        'url': download_url,
                        'width': width,
                        'height': height,
                        'exact_match': width == self.min_width and height == self.min_height
                    })
                    logging.debug(f"Found download option: {download_url} ({width}x{height})")
                except (ValueError, IndexError) as e:
                    logging.debug(f"Failed to parse resolution in {text}: {e}")
        
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
        
        # Strategy 2: If no links found, look for images that might be high resolution
        if not download_urls:
            logging.debug("Looking for large images")
            main_image = soup.find('img', class_=lambda c: c and ('wallpaper' in c or 'main' in c))
            
            if main_image and main_image.has_attr('src'):
                img_url = urljoin(self.BASE_URL, main_image['src'])
                logging.info(f"Found main image: {img_url}")
                download_urls.append(img_url)
        
        return download_urls