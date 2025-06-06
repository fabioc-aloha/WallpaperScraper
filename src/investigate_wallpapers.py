import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urljoin
import logging
from src.config import CONFIG

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Setup headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# Target parameters
theme = 'nature'
base_url = 'https://4kwallpapers.com'
theme_url = f'{base_url}/{theme}'

TEMP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'temp')
os.makedirs(TEMP_DIR, exist_ok=True)


def inspect_image_pages():
    # Fetch the category page
    logging.info(f"Fetching theme page: {theme_url}")
    resp = requests.get(theme_url, headers=headers)
    if resp.status_code != 200:
        logging.error(f"Failed to fetch page: {resp.status_code}")
        return

    soup = BeautifulSoup(resp.text, 'html.parser')

    # Save the theme page HTML for inspection
    with open(os.path.join(TEMP_DIR, 'theme_page.html'), 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    logging.info(
        f"Saved theme page HTML to {os.path.join(TEMP_DIR, 'theme_page.html')} for inspection")

    # Look for image thumbnails and check their parent links
    img_tags = soup.find_all('img')
    logging.info(f"Found {len(img_tags)} images on the page")
    for img in img_tags:
        if img.parent and img.parent.name == 'a':
            href = img.parent.get('href', '')
            logging.info(f"Image with parent link: {href}")
            logging.info(f"  Image alt: {img.get('alt', '')}")
            logging.info(f"  Image src: {img.get('src', '')}")
    # Look for links that might lead to individual wallpaper pages
    all_links = soup.find_all('a', href=True)
    logging.info(f"\nFound {len(all_links)} links on the theme page")

    wallpaper_pages = []  # <-- Fix: define the list before use
    for link in all_links:
        href = link['href']
        # Look for nature/something/123 pattern
        if href.startswith(
                f'/{theme}/') and href.count('/') >= 2 and href not in wallpaper_pages:
            wallpaper_pages.append(href)

    logging.info(f"Found {len(wallpaper_pages)} potential wallpaper pages")
    if not wallpaper_pages:
        logging.warning("No wallpaper detail pages found!")
        return

    # Display a few samples
    for i, page in enumerate(wallpaper_pages[:5]):
        logging.info(f"Sample {i+1}: {page}")

    # Visit the first detail page
    for detail_url in wallpaper_pages:
        logging.info(f"\nVisiting detail page: {detail_url}")

        detail_resp = requests.get(detail_url, headers=headers)
        if detail_resp.status_code == 200:
            # Save the detail page HTML for inspection
            with open(os.path.join(TEMP_DIR, 'detail_page.html'), 'w', encoding='utf-8') as f:
                f.write(detail_resp.text)
            logging.info(
                f"Saved detail page HTML to {os.path.join(TEMP_DIR, 'detail_page.html')} for inspection")

            detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')

            # Look for all <a> tags that might be download links
            all_links = detail_soup.find_all('a', href=True)
            download_links = []

            for link in all_links:
                href = link.get('href', '')
                text = link.get_text().strip()

                # Check if link text contains resolution pattern like
                # "1920x1080"
                if re.search(r'\d+\s*[xX]\s*\d+', text):
                    download_links.append((text, href))
                    logging.info(f"Potential download link: {text} -> {href}")

                # Check if link href contains resolution pattern
                elif re.search(r'\d+x\d+', href):
                    download_links.append((text, href))
                    logging.info(
                        f"Potential download link from href: {text} -> {href}")

            if not download_links:
                logging.info(
                    "\nNo standard download links found. Looking for alternative sources...")

                # Look for any direct links to image files
                img_links = detail_soup.find_all('a', href=lambda href: href and (
                    href.endswith('.jpg') or href.endswith('.jpeg') or href.endswith('.png')))
                for link in img_links:
                    href = link.get('href', '')
                    text = link.get_text().strip() or "Image link"
                    logging.info(f"Direct image link: {text} -> {href}")

            # Look for the main image on the page - sometimes it's the
            # highest resolution version
            main_img = detail_soup.find('img', class_='img-responsive')
            if main_img and main_img.has_attr('src'):
                logging.info(f"Main image: {main_img['src']}")

            # Look for text containing resolution information anywhere on
            # the page
            all_text = detail_soup.get_text()
            res_matches = re.findall(r'(\d+)\s*[xX]\s*(\d+)', all_text)
            logging.info(f"Found {len(res_matches)} resolution mentions in text:")
            for width, height in res_matches:
                logging.info(f"  {width}x{height}")


# Only run if this is the main script
if __name__ == '__main__':
    inspect_image_pages()
