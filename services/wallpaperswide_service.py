"""
Service module for fetching wallpapers from wallpaperswide.com.
"""
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import logging
from config import CONFIG
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
            self.min_width = self.min_height = 0

        # More comprehensive browser headers to avoid being detected as a bot
        self.headers = {
            'User-Agent': CONFIG['USER_AGENT'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def fetch_wallpapers(self):
        """
        Fetch wallpaper download URLs by theme and resolution.
        
        Returns:
            List of wallpaper download URLs matching the requested criteria.
        """
        wallpapers = []

        # This site allows direct resolution filtering via URL
        resolution_url = f"{self.resolution}-wallpapers-r.html"
        
        # Process each theme
        for theme in self.themes:
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
        
        # Remove duplicates while preserving order
        unique_wallpapers = []
        seen = set()
        for url in wallpapers:
            if url not in seen:
                seen.add(url)
                unique_wallpapers.append(url)
        
        logging.info(f"Found {len(unique_wallpapers)} unique wallpapers from wallpaperswide.com")
        return unique_wallpapers
    
    def _process_theme_page(self, url):
        """
        Process a theme page to find wallpaper detail pages.
        
        Args:
            url: The URL of the theme page
            
        Returns:
            List of wallpaper download URLs
        """
        wallpapers = []
        timeout = CONFIG.get('REQUEST_TIMEOUT', 10)
        max_retries = CONFIG.get('MAX_RETRIES', 3)
        retry_delay = CONFIG.get('RETRY_DELAY', 1)
        
        # Use retry logic for resilience
        for attempt in range(max_retries):
            try:
                resp = requests.get(url, headers=self.headers, timeout=timeout)
                resp.raise_for_status()  # Raise exception for 4XX/5XX responses
                break
            except (requests.RequestException, IOError) as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                    logging.warning(f"Attempt {attempt+1} failed for {url}: {e}. Retrying in {wait_time}s")
                    time.sleep(wait_time)
                else:
                    logging.error(f"Failed to fetch {url} after {max_retries} attempts: {e}")
                    return []
        
        # If we get here without a successful response, return empty list
        if not hasattr(resp, 'text') or resp.status_code != 200:
            return []
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        wallpaper_links = []
        
        # Look for thumbnails with links to detail pages
        thumbnails = []
        
        # First try to find image tags inside links
        for img in soup.find_all('img'):
            parent = img.find_parent('a')
            if parent and parent.has_attr('href') and 'wallpaper' in parent['href']:
                thumbnails.append(parent['href'])
        
        # If that doesn't work, try looking for links with wallpaper in them
        if not thumbnails:
            for link in soup.find_all('a', href=True):
                if 'wallpaper' in link['href'] and not link['href'].startswith('http'):
                    # Skip category navigation links
                    if not link['href'].endswith('.html'):
                        continue
                    thumbnails.append(link['href'])
        
        # Limit to first N thumbnails per page to avoid excessive requests
        max_items = CONFIG.get('MAX_ITEMS_PER_THEME', 10)
        for link in thumbnails[:max_items]:
            detail_url = urljoin(self.BASE_URL, link)
            try:
                download_links = self._process_detail_page(detail_url)
                wallpapers.extend(download_links)
            except Exception as e:
                logging.error(f"Error processing detail page {detail_url}: {e}")
            
            # Delay between requests
            time.sleep(CONFIG.get('REQUEST_DELAY', 1))
        
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
