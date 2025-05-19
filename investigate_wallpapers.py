import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urljoin

# Setup headers to mimic a browser
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

# Target parameters
theme = 'nature'
base_url = 'https://4kwallpapers.com'
theme_url = f'{base_url}/{theme}'

def inspect_image_pages():
    # Fetch the category page
    print(f"Fetching theme page: {theme_url}")
    resp = requests.get(theme_url, headers=headers)
    if resp.status_code != 200:
        print(f"Failed to fetch page: {resp.status_code}")
        return
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Save the theme page HTML for inspection
    with open('theme_page.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print(f"Saved theme page HTML to theme_page.html for inspection")
    
    # Look for image thumbnails and check their parent links
    img_tags = soup.find_all('img')
    print(f"Found {len(img_tags)} images on the page")
    
    wallpaper_pages = []
    for img in img_tags:
        # Find parent <a> tag if it exists
        parent_a = img.find_parent('a')
        if parent_a and parent_a.has_attr('href'):
            href = parent_a['href']
            if href.startswith(f'/{theme}/'):
                wallpaper_pages.append(href)
                print(f"Image with parent link: {href}")
                print(f"  Image alt: {img.get('alt', '')}")
                print(f"  Image src: {img.get('src', '')}")
    
    # Look for links that might lead to individual wallpaper pages
    all_links = soup.find_all('a', href=True)
    print(f"\nFound {len(all_links)} links on the theme page")
    
    for link in all_links:
        href = link['href']
        # Look for nature/something/123 pattern
        if href.startswith(f'/{theme}/') and href.count('/') >= 2 and href not in wallpaper_pages:
            wallpaper_pages.append(href)
    
    print(f"Found {len(wallpaper_pages)} potential wallpaper pages")
    if not wallpaper_pages:
        print("No wallpaper detail pages found!")
        return
    
    # Display a few samples
    for i, page in enumerate(wallpaper_pages[:5]):
        print(f"Sample {i+1}: {page}")
    
    # Visit the first detail page
    if wallpaper_pages:
        detail_url = urljoin(base_url, wallpaper_pages[0])
        print(f"\nVisiting detail page: {detail_url}")
        
        detail_resp = requests.get(detail_url, headers=headers)
        if detail_resp.status_code == 200:
            # Save the detail page HTML for inspection
            with open('detail_page.html', 'w', encoding='utf-8') as f:
                f.write(detail_resp.text)
            print(f"Saved detail page HTML to detail_page.html for inspection")
            
            detail_soup = BeautifulSoup(detail_resp.text, 'html.parser')
            
            # Look for all <a> tags that might be download links
            all_links = detail_soup.find_all('a', href=True)
            download_links = []
            
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text().strip()
                
                # Check if link text contains resolution pattern like "1920x1080"
                if re.search(r'\d+\s*[xX]\s*\d+', text):
                    download_links.append((text, href))
                    print(f"Potential download link: {text} -> {href}")
                
                # Check if link href contains resolution pattern
                elif re.search(r'\d+x\d+', href):
                    download_links.append((text, href))
                    print(f"Potential download link from href: {text} -> {href}")
            
            if not download_links:
                print("\nNo standard download links found. Looking for alternative sources...")
                
                # Look for any direct links to image files
                img_links = detail_soup.find_all('a', href=lambda href: href and (href.endswith('.jpg') or href.endswith('.jpeg') or href.endswith('.png')))
                for link in img_links:
                    href = link.get('href', '')
                    text = link.get_text().strip() or "Image link"
                    print(f"Direct image link: {text} -> {href}")
                    
                # Look for the main image on the page - sometimes it's the highest resolution version
                main_img = detail_soup.find('img', class_='img-responsive')
                if main_img and main_img.has_attr('src'):
                    print(f"Main image: {main_img['src']}")
                
                # Look for text containing resolution information anywhere on the page
                all_text = detail_soup.get_text()
                res_matches = re.findall(r'(\d+)\s*[xX]\s*(\d+)', all_text)
                print(f"Found {len(res_matches)} resolution mentions in text:")
                for width, height in res_matches:
                    print(f"  {width}x{height}")

# Run the inspection
inspect_image_pages()
