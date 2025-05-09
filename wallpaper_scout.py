#!/usr/bin/env python
"""
Wallpaper Scout Script

This script explores the supported wallpaper sites to discover available themes,
resolutions, and other useful information. It generates a SITES.md file with this
information to help with configuration decisions.

Usage:
    python wallpaper_scout.py
"""

import os
import re
import requests
from bs4 import BeautifulSoup
import logging
import sys
import time
from urllib.parse import urljoin
import markdown
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import datetime

from config import CONFIG
from services.wallpaperswide_service import WallpapersWideService
from services.wallhaven_service import WallhavenService
from services.wallpaperbat_service import WallpaperBatService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

class WallpaperScout:
    """Explores wallpaper sites for themes and other information."""
    
    def __init__(self):
        """Initialize the scout with common headers."""
        self.headers = {
            'User-Agent': CONFIG['USER_AGENT'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }
        self.timeout = CONFIG['REQUEST_TIMEOUT']
        self.retry_delay = CONFIG['RETRY_DELAY']
        self.max_retries = CONFIG['MAX_RETRIES']
        self.output_file = "SITES.md"

    def _fetch_with_retry(self, url):
        """Fetch a URL with retry logic."""
        for attempt in range(self.max_retries):
            try:
                resp = requests.get(url, headers=self.headers, timeout=self.timeout)
                if resp.status_code == 200:
                    return resp
                logging.warning(f"HTTP {resp.status_code} from {url}")
            except Exception as e:
                logging.warning(f"Error fetching {url}: {e}")
            
            wait_time = self.retry_delay * (2 ** attempt)
            logging.debug(f"Retrying in {wait_time}s...")
            time.sleep(wait_time)
        
        logging.error(f"Failed to fetch {url} after {self.max_retries} attempts")
        return None

    def scout_wallpaperswide(self):
        """Scout information from wallpaperswide.com"""
        site_info = {
            'name': 'WallpapersWide',
            'url': 'https://wallpaperswide.com',
            'themes': [],
            'resolutions': [],
            'categories': [],
            'description': 'Offers a wide variety of wallpapers with direct resolution filtering.'
        }
        
        # Fetch the main page to extract categories
        resp = self._fetch_with_retry(site_info['url'])
        if not resp:
            return site_info
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Extract categories
        menu_items = soup.select('div.wallpapers-menu-items a')
        for item in menu_items:
            if item.text.strip() and 'wallpaper' in item.get('href', ''):
                category = item.text.strip()
                site_info['categories'].append(category)
                # Use category as theme if it looks like one
                if not any(x in category.lower() for x in ['page', 'top', 'latest', 'popular', 'random']):
                    site_info['themes'].append(category)
        
        # Extract available resolutions
        resolution_section = soup.select_one('div.resolutions')
        if resolution_section:
            resolution_links = resolution_section.select('a')
            for link in resolution_links:
                res_text = link.text.strip()
                if 'x' in res_text:
                    site_info['resolutions'].append(res_text)
        
        # If no themes were found, add some common themes that are known to work
        if not site_info['themes']:
            common_themes = [
                'Nature', 'Abstract', 'Space', 'City', 'Animals', 'Landscape', 
                'Flowers', 'Beach', 'Mountains', 'Fantasy', 'Art', 'Sunset', 
                'Ocean', 'Digital Art', 'Wildlife', 'Architecture'
            ]
            site_info['themes'] = common_themes
                    
        # Clean up themes
        site_info['themes'] = sorted(list(set(site_info['themes'])))
        
        return site_info

    def scout_wallhaven(self):
        """Scout information from wallhaven.cc"""
        site_info = {
            'name': 'Wallhaven',
            'url': 'https://wallhaven.cc',
            'themes': [],
            'resolutions': [],
            'categories': ['General', 'Anime', 'People'],
            'description': 'Community-driven collection with advanced filtering and tagging system.'
        }
        
        # Fetch the tags page to extract themes
        tags_url = urljoin(site_info['url'], '/tags')
        resp = self._fetch_with_retry(tags_url)
        if not resp:
            return site_info
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Extract popular tags which make good themes
        tag_items = soup.select('a.tag')
        for tag in tag_items[:50]:  # Limit to top 50 tags
            tag_text = tag.text.strip()
            if tag_text and len(tag_text) > 1:
                site_info['themes'].append(tag_text)
        
        # Extract available resolutions from the search page
        search_url = urljoin(site_info['url'], '/search')
        resp = self._fetch_with_retry(search_url)
        if resp:
            soup = BeautifulSoup(resp.text, 'html.parser')
            resolution_options = soup.select('select[name="resolutions"] option')
            for option in resolution_options:
                res_text = option.text.strip()
                if res_text and 'x' in res_text and not res_text.startswith('At least'):
                    site_info['resolutions'].append(res_text)
        
        # If no themes were found, add some common tags that are known to work on wallhaven
        if not site_info['themes']:
            common_themes = [
                'landscape', 'nature', 'digital art', 'fantasy', 'space', 
                'mountains', 'forest', 'anime', 'artwork', 'sky', 'sunset', 
                'cyberpunk', 'minimalism', 'city', 'night', 'abstract'
            ]
            site_info['themes'] = common_themes
        
        # Clean up themes
        site_info['themes'] = sorted(list(set(site_info['themes'])))
        
        return site_info

    def scout_wallpaperbat(self):
        """Scout information from wallpaperbat.com"""
        site_info = {
            'name': 'WallpaperBat',
            'url': 'https://wallpaperbat.com',
            'themes': [],
            'resolutions': [],
            'categories': [],
            'description': 'Collection including super ultrawide (5120x1440) wallpapers.'
        }
        
        # Fetch the main page
        resp = self._fetch_with_retry(site_info['url'])
        if not resp:
            return site_info
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Extract categories which can be used as themes
        menu_items = soup.select('a.nav-link')
        for item in menu_items:
            category = item.text.strip()
            if category and not any(x in category.lower() for x in ['home', 'contact', 'about', 'privacy']):
                site_info['categories'].append(category)
                site_info['themes'].append(category)
        
        # Look for resolution options or popular resolution pages
        resolution_links = soup.select('a[href*="x"]')
        for link in resolution_links:
            href = link.get('href', '')
            res_match = re.search(r'(\d+)x(\d+)', href)
            if res_match:
                resolution = f"{res_match.group(1)}x{res_match.group(2)}"
                if resolution not in site_info['resolutions']:
                    site_info['resolutions'].append(resolution)
        
        # Also check search pages for popular categories
        popular_searches = []
        search_items = soup.select('a[href*="search"]')
        for item in search_items:
            search_text = item.text.strip()
            if search_text and len(search_text) > 2 and search_text not in popular_searches:
                popular_searches.append(search_text)
                site_info['themes'].append(search_text)
        
        # If no themes or resolutions were found, add some known ones
        if not site_info['themes']:
            common_themes = [
                'Nature', '4K', 'Gaming', 'Anime', 'Abstract', 'Minimal', 
                'Dark', 'Space', 'Landscape', 'Desktop', 'Ultrawide', 'Dual Monitor'
            ]
            site_info['themes'] = common_themes
            
        if not site_info['resolutions']:
            site_info['resolutions'] = ['5120x1440', '3840x1080', '3440x1440', '2560x1080', '1920x1080']
        
        # Clean up themes
        site_info['themes'] = sorted(list(set([t for t in site_info['themes'] if len(t) > 2])))
        site_info['resolutions'] = sorted(list(set(site_info['resolutions'])))
        
        return site_info

    def generate_report(self, sites_info):
        """Generate a markdown report with the collected information."""
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        md_content = f"""# Wallpaper Sites Report
*Generated on: {now}*

This report contains information about wallpaper sites supported by the Wallpaper Scraper tool,
including available themes, resolutions, and other useful details to help with configuration.

## Summary

| Site | Themes | Resolutions | URL |
|------|--------|-------------|-----|
"""
        
        # Add summary for each site
        for site in sites_info:
            theme_count = len(site['themes'])
            res_count = len(site['resolutions'])
            md_content += f"| {site['name']} | {theme_count} | {res_count} | {site['url']} |\n"
        
        # Add common themes section - gather themes that appear in multiple sites
        all_themes = {}
        for site in sites_info:
            for theme in site['themes']:
                theme_lower = theme.lower()
                if theme_lower in all_themes:
                    all_themes[theme_lower]['count'] += 1
                    all_themes[theme_lower]['sites'].append(site['name'])
                else:
                    all_themes[theme_lower] = {
                        'name': theme,
                        'count': 1,
                        'sites': [site['name']]
                    }
        
        # Filter to themes available on multiple sites
        common_themes = [theme_data for theme_data in all_themes.values() 
                         if theme_data['count'] > 1]
        
        if common_themes:
            md_content += "\n## Common Themes Across Sites\n\n"
            md_content += "These themes are available on multiple sites, making them good choices for your configuration:\n\n"
            
            # Sort by count (highest first) then alphabetically
            sorted_common = sorted(common_themes, 
                                  key=lambda x: (-x['count'], x['name'].lower()))
            
            for theme_data in sorted_common[:15]:  # Limit to top 15
                sites_list = ', '.join(theme_data['sites'])
                md_content += f"- **{theme_data['name']}** - Available on: {sites_list}\n"
                
            md_content += "\n"
            
        # Add top resolution section
        all_resolutions = {}
        for site in sites_info:
            for res in site['resolutions']:
                # Extract just the dimensions, ignore aspect ratio prefix if present
                match = re.search(r'(\d+x\d+)', res)
                if match:
                    pure_res = match.group(1)
                    if pure_res in all_resolutions:
                        all_resolutions[pure_res]['count'] += 1
                        all_resolutions[pure_res]['sites'].append(site['name'])
                    else:
                        all_resolutions[pure_res] = {
                            'name': pure_res,
                            'count': 1,
                            'sites': [site['name']]
                        }
        
        # Add popular resolutions section
        if all_resolutions:
            md_content += "\n## Popular Resolutions\n\n"
            
            # Sort by popularity of common monitor resolutions
            popular_res = ['5120x1440', '3440x1440', '2560x1440', '3840x2160', '1920x1080']
            
            for res in popular_res:
                if res in all_resolutions:
                    sites_list = ', '.join(all_resolutions[res]['sites'])
                    md_content += f"- **{res}** - Available on: {sites_list}\n"
                    
            md_content += "\n"
        
        # Add detailed section for each site
        md_content += "\n## Site Details\n\n"
        
        for site in sites_info:
            md_content += f"### {site['name']}\n\n"
            md_content += f"**URL:** {site['url']}  \n"
            md_content += f"**Description:** {site['description']}  \n\n"
            
            if site['categories']:
                md_content += "**Categories:**  \n"
                for cat in site['categories']:
                    md_content += f"- {cat}  \n"
                md_content += "\n"
            
            if site['resolutions']:
                md_content += "**Available Resolutions:**  \n"
                # Show resolutions in a multi-column format
                res_chunks = [site['resolutions'][i:i+5] for i in range(0, len(site['resolutions']), 5)]
                for chunk in res_chunks:
                    md_content += "- " + ", ".join(chunk) + "  \n"
                md_content += "\n"
            
            if site['themes']:
                md_content += "**Recommended Themes:**  \n"
                # Show themes in a multi-column format
                theme_chunks = [site['themes'][i:i+5] for i in range(0, len(site['themes']), 5)]
                for chunk in theme_chunks:
                    md_content += "- " + ", ".join(chunk) + "  \n"
                md_content += "\n"
            
            md_content += "\n"
        
        # Add configuration recommendations
        md_content += """## Configuration Recommendations

To update your configuration based on this report, modify `config.py` with your preferred themes and resolution:

```python
CONFIG = {
    'RESOLUTION': '5120x1440',  # Choose from available resolutions
    'THEMES': ['nature', 'abstract', 'space'],  # Choose from recommended themes
    'SITES': ['wallpaperswide.com', 'wallhaven.cc', 'wallpaperbat.com'],
    # ... other configuration options
}
```

For best results:
1. Choose 3-5 themes maximum to avoid excessive downloads
2. Select the exact resolution for your displays
3. Enable all sites for maximum variety

> Note: Some sites may not have every theme or resolution listed. The scraper will try to find the closest match.
"""

        # Add sample URLs section
        md_content += "\n## Sample URLs\n\n"
        md_content += "Here are some sample URLs you can explore directly:\n\n"
        
        for site in sites_info:
            if site['name'] == 'WallpapersWide':
                md_content += f"- WallpapersWide Nature 5120x1440: {site['url']}/5120x1440-nature-wallpapers-r.html\n"
            elif site['name'] == 'Wallhaven':
                md_content += f"- Wallhaven Landscape Search: {site['url']}/search?q=landscape&categories=111&purity=100&sorting=relevance\n"
            elif site['name'] == 'WallpaperBat':
                md_content += f"- WallpaperBat Ultrawide: {site['url']}/top-ultrawide-wallpapers\n"
                
        # Write to the output file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logging.info(f"Report generated: {os.path.abspath(self.output_file)}")
        return md_content

    def run(self):
        """Run the scout on all supported sites."""
        logging.info("Starting wallpaper scout...")
        
        sites_info = []
        
        # Set up parallel execution for faster scouting
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all scouting tasks
            scout_tasks = {
                executor.submit(self.scout_wallpaperswide): "WallpapersWide",
                executor.submit(self.scout_wallhaven): "Wallhaven",
                executor.submit(self.scout_wallpaperbat): "WallpaperBat"
            }
            
            # Process results as they complete
            for future in tqdm(as_completed(scout_tasks), total=len(scout_tasks), desc="Scouting sites"):
                site_name = scout_tasks[future]
                try:
                    site_info = future.result()
                    logging.info(f"Found {len(site_info['themes'])} themes and {len(site_info['resolutions'])} resolutions on {site_name}")
                    sites_info.append(site_info)
                except Exception as e:
                    logging.error(f"Error scouting {site_name}: {e}")
        
        # Generate the report
        self.generate_report(sites_info)
        
        logging.info("Wallpaper scout completed.")
        return True


if __name__ == "__main__":
    try:
        scout = WallpaperScout()
        success = scout.run()
        if success:
            print(f"✅ Successfully created {scout.output_file}")
            print(f"   Path: {os.path.abspath(scout.output_file)}")
        else:
            print(f"❌ Failed to create {scout.output_file}")
    except Exception as e:
        print(f"❌ Error running wallpaper scout: {e}")
        import traceback
        traceback.print_exc()
