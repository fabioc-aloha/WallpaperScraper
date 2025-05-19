import requests
import time
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

# Setup headers to mimic a browser with more complete information
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# Target parameters
base_url = 'https://wallpaperswide.com'

def inspect_wallpaperswide():
    # Try multiple approaches
    approaches = [
        {'type': 'resolution', 'url': f'{base_url}/5120x1440-wallpapers-r.html'},
        {'type': 'category', 'url': f'{base_url}/nature-desktop-wallpapers.html'},
        {'type': 'homepage', 'url': f'{base_url}'}
    ]
    
    for approach in approaches:
        print(f"\n=== Trying approach: {approach['type']} ===")
        search_url = approach['url']
        print(f"Fetching page: {search_url}")
        
        try:
            # Add delay between requests to avoid rate limiting
            time.sleep(2)
            resp = requests.get(search_url, headers=headers, timeout=10)
            
            print(f"Status code: {resp.status_code}")
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Save HTML for inspection
                filename = f"wallpaperswide_{approach['type']}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(resp.text)
                print(f"Saved HTML to {filename}")
                
                print(f"Page title: {soup.title.text if soup.title else 'No title'}")
                print(f"Page size: {len(resp.text)} characters")
                
                # Print the first 200 characters to see if the response is valid HTML
                print("Response preview:")
                preview = resp.text[:200].replace('\n', ' ')
                print(preview)
                
                # Try to identify wallpaper elements
                print("\nLooking for common elements...")
                element_counts = {
                    'img': len(soup.find_all('img')),
                    'a': len(soup.find_all('a', href=True)),
                    'div': len(soup.find_all('div')),
                    'ul': len(soup.find_all('ul')),
                    'li': len(soup.find_all('li'))
                }
                
                for elem, count in element_counts.items():
                    print(f"- {elem}: {count}")
                
                # Look for wallpaper links using various selectors
                print("\nSearching for wallpaper links...")
                wallpaper_links = []
                
                # Try to find links within standard patterns
                links_with_wallpaper = soup.find_all('a', href=lambda href: href and ('/wallpaper/' in href or '/wallpapers/' in href))
                print(f"Links containing 'wallpaper' in href: {len(links_with_wallpaper)}")
                
                if links_with_wallpaper:
                    for i, link in enumerate(links_with_wallpaper[:5]):
                        href = link.get('href', '')
                        print(f"  Link {i+1}: {href}")
                        wallpaper_links.append(href)
                
                # If no direct links found, try image parents
                if not wallpaper_links:
                    for img in soup.find_all('img'):
                        parent = img.find_parent('a')
                        if parent and parent.has_attr('href'):
                            href = parent['href']
                            # Skip navigation links that might have images
                            if 'wallpaper' in href or 'image' in href:
                                wallpaper_links.append(href)
                                print(f"Found via image parent: {href}")
                                if len(wallpaper_links) >= 5:
                                    break
                
                # Visit a detail page if found
                if wallpaper_links:
                    # Get the first full link
                    detail_url = urljoin(base_url, wallpaper_links[0])
                    print(f"\nVisiting detail page: {detail_url}")
                    
                    try:
                        # Add delay to avoid rate limiting
                        time.sleep(2)
                        detail_resp = requests.get(detail_url, headers=headers, timeout=10)
                        print(f"Detail page status: {detail_resp.status_code}")
                        
                        if detail_resp.status_code == 200:
                            detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
                            
                            # Save detail HTML
                            detail_filename = f"wallpaperswide_detail_{approach['type']}.html"
                            with open(detail_filename, 'w', encoding='utf-8') as f:
                                f.write(detail_resp.text)
                            print(f"Saved detail HTML to {detail_filename}")
                            
                            # Look for download links
                            print("\nLooking for download links...")
                            
                            # Try different selectors for download links
                            download_selectors = [
                                '.resolutions a',  # Common pattern
                                '.download',
                                'a[href*="download"]',
                                'a[href*=".jpg"]',
                                'a[href*="wallpaper-download"]'
                            ]
                            
                            for selector in download_selectors:
                                links = detail_soup.select(selector)
                                print(f"Selector '{selector}': {len(links)} links")
                                
                                for i, link in enumerate(links[:3]):
                                    href = link.get('href', '')
                                    text = link.get_text().strip()
                                    print(f"  Link {i+1}: [{text}] -> {href}")
                                    
                                    # Look for resolution information
                                    res_match = re.search(r'(\d+)\s*[xX]\s*(\d+)', text)
                                    if res_match:
                                        print(f"    Found resolution: {res_match.group(0)}")
                            
                            # If no standard download links, look for embedded images
                            main_images = detail_soup.select('.wallpaper-preview img') or detail_soup.select('.main-wallpaper img')
                            if main_images:
                                print("\nFound main wallpaper images:")
                                for i, img in enumerate(main_images[:2]):
                                    print(f"  Image {i+1}: {img.get('src', '')}")
                                    
                    except Exception as e:
                        print(f"Error fetching detail page: {e}")
                
                # If we found wallpaper links, we've succeeded with this approach
                if wallpaper_links:
                    break
            else:
                print(f"Failed to fetch page: {resp.status_code}")
                
        except Exception as e:
            print(f"Error during {approach['type']} approach: {e}")

# Run the inspection
inspect_wallpaperswide()
