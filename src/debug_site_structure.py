import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from bs4 import BeautifulSoup
import os
import logging
from src.config import CONFIG

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Setup headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
url = 'https://4kwallpapers.com/nature'

TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)

response = None
soup = None

try:
    logging.info(f"Fetching {url}")
    response = requests.get(url, headers=headers)
    logging.info(f"Status code: {response.status_code}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check for common elements
        if soup:
            logging.info(f"Title: {soup.title.text if soup.title else 'No title found'}")
            logging.info(f"Number of images: {len(soup.find_all('img'))}")

        # Try different selectors to find thumbnail links
        selectors = [
            'figure.wallpapers__item',  # Original selector
            'figure',
            'article',
            '.thumb',
            '.gallery',
            '.wallpaper',
            'a[href*="wallpaper"]'
        ]

        for selector in selectors:
            elements = soup.select(selector)
            logging.info(f"\nSelector '{selector}' found {len(elements)} elements")
            if elements and len(elements) > 0:
                logging.info(f"First element: {elements[0]}")

        # Look at the first few links to find potential wallpaper detail pages
        wallpaper_links = []
        all_links = soup.find_all('a', href=True)
        logging.info(f"\nFound {len(all_links)} total links on the page")

        for link in all_links[:50]:  # Check first 50 links
            href = link.get('href', '')
            if '/wallpaper/' in href or '/images/' in href:
                wallpaper_links.append(href)

        logging.info(f"Found {len(wallpaper_links)} potential wallpaper detail links")
        for link in wallpaper_links[:5]:  # Show first 5
            logging.info(f"  - {link}")

        # If we found potential links, visit the first one
        if wallpaper_links:
            detail_url = wallpaper_links[0]
            if not detail_url.startswith('http'):
                detail_url = f"https://4kwallpapers.com{detail_url}"

            logging.info(f"\nVisiting detail page: {detail_url}")
            detail_response = requests.get(detail_url, headers=headers)
            if detail_response.status_code == 200:
                detail_soup = BeautifulSoup(detail_response.text, 'html.parser')

                # Look for download links with various selectors
                download_selectors = [
                    'a.download__link',
                    'a[href*="download"]',
                    'a[href*=".jpg"]',
                    'a[href*=".png"]'
                ]

                for selector in download_selectors:
                    download_links = detail_soup.select(selector)
                    logging.info(
                        f"Download selector '{selector}' found {len(download_links)} links")
                    if download_links:
                        for dl in download_links[:3]:  # Show up to 3
                            logging.info(f"  - {dl}")
except Exception as e:
    logging.error(f"An error occurred: {e}")
