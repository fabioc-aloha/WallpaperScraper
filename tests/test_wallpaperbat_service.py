"""
Tests for the WallpaperBatService class
"""
import unittest
from unittest.mock import patch, MagicMock
import requests
import sys
import os
import tempfile
import io
from PIL import Image
import io

# Add the parent directory to sys.path to be able to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from services.wallpaperbat_service import WallpaperBatService


class TestWallpaperBatService(unittest.TestCase):
    """Test case for the WallpaperBatService class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = WallpaperBatService(resolution="5120x1440", themes=["nature"])
        
    def test_init(self):
        """Test service initialization"""
        self.assertEqual(self.service.resolution, "5120x1440")
        self.assertEqual(self.service.themes, ["nature"])
        self.assertEqual(self.service.min_width, 5120)
        self.assertEqual(self.service.min_height, 1440)
        
    @patch('services.wallpaperbat_service.requests.get')
    def test_fetch_with_retry_success(self, mock_get):
        """Test successful request with retry logic"""
        # Create a mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Call the method
        response = self.service._fetch_with_retry('https://example.com')
        
        # Assert the result
        self.assertEqual(response, mock_response)
        mock_get.assert_called_once()
        
    @patch('services.wallpaperbat_service.requests.get')
    def test_fetch_with_retry_failure(self, mock_get):
        """Test failed request with retry logic"""
        # Make the request fail
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        # Call the method
        response = self.service._fetch_with_retry('https://example.com')
        
        # Assert the result
        self.assertIsNone(response)
        self.assertEqual(mock_get.call_count, 3)  # Default max_retries is 3
        
    @patch('services.wallpaperbat_service.WallpaperBatService._process_search_page')
    def test_fetch_wallpapers(self, mock_process_search):
        """Test fetching wallpapers"""
        # Setup mock return values
        mock_process_search.return_value = ['https://example.com/wallpaper1.jpg', 'https://example.com/wallpaper2.jpg']
        
        # Call the method
        wallpapers = self.service.fetch_wallpapers()
        
        # Assert the result
        self.assertEqual(len(wallpapers), 2)
        self.assertIn('https://example.com/wallpaper1.jpg', wallpapers)
        self.assertIn('https://example.com/wallpaper2.jpg', wallpapers)
        
        # Verify the search page was processed
        self.assertTrue(mock_process_search.called)
        
    @patch('services.wallpaperbat_service.WallpaperBatService._fetch_with_retry')
    def test_process_detail_page_with_exact_match(self, mock_fetch):
        """Test processing a detail page with an exact resolution match"""
        # Create mock HTML with an image matching our resolution
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <body>
                <img class="img-wallpaper" src="https://example.com/wallpaper-5120x1440.jpg" 
                     width="5120" height="1440" alt="Wallpaper">
                <a class="download-button" href="https://example.com/download/wallpaper-5120x1440.jpg">
                    Download 5120 x 1440
                </a>
            </body>
        </html>
        '''
        mock_fetch.return_value = mock_response
        
        # Call the method
        download_urls = self.service._process_detail_page('https://example.com/wallpaper.html')
        
        # Assert the result
        self.assertEqual(len(download_urls), 1)
        self.assertEqual(download_urls[0], 'https://example.com/wallpaper-5120x1440.jpg')
        
    def test_image_resolution_handling(self):
        """Test that the service correctly handles images with different resolutions"""
        # Create a test image with resolution that's too small
        small_img = Image.new('RGB', (800, 600), color='red')
        small_img_bytes = io.BytesIO()
        small_img.save(small_img_bytes, format='JPEG')
        small_img_bytes = small_img_bytes.getvalue()
        
        # Create a test image with the right resolution
        correct_img = Image.new('RGB', (5120, 1440), color='blue')
        correct_img_bytes = io.BytesIO()
        correct_img.save(correct_img_bytes, format='JPEG')
        correct_img_bytes = correct_img_bytes.getvalue()
        
        # Mock response for detail page with both image options
        mock_detail_html = f"""
        <html>
            <body>
                <img class="img-wallpaper" src="https://example.com/small.jpg" width="800" height="600" />
                <a class="download-button" href="https://example.com/correct.jpg">Download 5120x1440</a>
            </body>
        </html>
        """
        
        # Setup the mock responses
        mock_response_detail = MagicMock()
        mock_response_detail.status_code = 200
        mock_response_detail.text = mock_detail_html
        
        mock_response_small = MagicMock()
        mock_response_small.status_code = 200
        mock_response_small.content = small_img_bytes
        
        mock_response_correct = MagicMock()
        mock_response_correct.status_code = 200
        mock_response_correct.content = correct_img_bytes
        
        # Setup the mock get to return different responses based on URL
        def mock_get(url, **kwargs):
            if url == "https://example.com/detail.html":
                return mock_response_detail
            elif url == "https://example.com/small.jpg":
                return mock_response_small
            elif url == "https://example.com/correct.jpg":
                return mock_response_correct
            return MagicMock(status_code=404)
            
        # Test the service with the mocks
        with patch('services.wallpaperbat_service.requests.get', side_effect=mock_get):
            # Process the detail page
            service = WallpaperBatService(resolution="5120x1440")
            download_urls = service._process_detail_page("https://example.com/detail.html")
            
            # Should prefer the higher resolution option when available
            self.assertEqual(len(download_urls), 1)
            self.assertEqual(download_urls[0], "https://example.com/correct.jpg")

if __name__ == '__main__':
    unittest.main()
