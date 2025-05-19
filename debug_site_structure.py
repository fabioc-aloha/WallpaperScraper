import requests
from bs4 import BeautifulSoup

# Setup headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
url = 'https://4kwallpapers.com/nature'

print(f"Fetching {url}")
resp = requests.get(url, headers=headers)
print(f"Status code: {resp.status_code}")

if resp.status_code == 200:
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Check for common elements
    print(f"Title: {soup.title.text if soup.title else 'No title found'}")
    print(f"Number of images: {len(soup.find_all('img'))}")
    
    # Try different selectors to find thumbnail links
    selectors_to_try = [
        'figure.wallpapers__item',  # Original selector
        'figure', 
        'article',
        '.thumb',
        '.gallery',
        '.wallpaper',
        'a[href*="wallpaper"]'
    ]
    
    for selector in selectors_to_try:
        elements = soup.select(selector)
        print(f"\nSelector '{selector}' found {len(elements)} elements")
        if elements and len(elements) > 0:
            print(f"First element: {elements[0]}")
    
    # Look at the first few links to find potential wallpaper detail pages
    wallpaper_links = []
    all_links = soup.find_all('a', href=True)
    print(f"\nFound {len(all_links)} total links on the page")
    
    for link in all_links[:50]:  # Check first 50 links
        href = link.get('href', '')
        if '/wallpaper/' in href or '/images/' in href:
            wallpaper_links.append(href)
    
    print(f"Found {len(wallpaper_links)} potential wallpaper detail links")
    for link in wallpaper_links[:5]:  # Show first 5
        print(f"  - {link}")
        
    # If we found potential links, visit the first one
    if wallpaper_links:
        detail_url = wallpaper_links[0]
        if not detail_url.startswith('http'):
            detail_url = f"https://4kwallpapers.com{detail_url}"
        
        print(f"\nVisiting detail page: {detail_url}")
        detail_resp = requests.get(detail_url, headers=headers)
        if detail_resp.status_code == 200:
            detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
            
            # Look for download links with various selectors
            download_selectors = [
                'a.download__link',
                'a[href*="download"]',
                'a[href*=".jpg"]',
                'a[href*=".png"]'
            ]
            
            for selector in download_selectors:
                download_links = detail_soup.select(selector)
                print(f"Download selector '{selector}' found {len(download_links)} links")
                if download_links:
                    for dl in download_links[:3]:  # Show up to 3
                        print(f"  - {dl}")
else:
    print(f"Failed to fetch page: {resp.status_code}")
