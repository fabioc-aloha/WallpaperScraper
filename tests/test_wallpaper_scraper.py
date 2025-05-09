import os
import tempfile
import unittest
from unittest.mock import patch, Mock
from PIL import Image
import sys
import io

# Import the check_image_resolution function
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from wallpaper_scraper import check_image_resolution, download_image

class TestWallpaperScraper(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for downloads
        self.tmpdir = tempfile.mkdtemp()
        self.test_url = 'https://example.com/test_image.jpg'
        self.headers = {'User-Agent': 'test-agent'}

    def tearDown(self):
        # Remove all files in the temp directory
        for fname in os.listdir(self.tmpdir):
            os.remove(os.path.join(self.tmpdir, fname))
        os.rmdir(self.tmpdir)

    def test_download_image_success(self):
        # Mock a successful HTTP response
        mock_resp = Mock(status_code=200, content=b'data')
        with patch('wallpaper_scraper.requests.get', return_value=mock_resp):
            result = download_image(
                url=self.test_url,
                output_folder=self.tmpdir,
                timeout=1,
                retries=1,
                delay=0,
                headers=self.headers
            )
            # Download should succeed and file should exist
            self.assertTrue(result)
            saved_file = os.path.join(self.tmpdir, os.path.basename(self.test_url))
            self.assertTrue(os.path.exists(saved_file))

    def test_download_image_failure(self):
        # Mock HTTP failures
        mock_resp = Mock(status_code=500)
        with patch('wallpaper_scraper.requests.get', return_value=mock_resp):
            result = download_image(
                url=self.test_url,
                output_folder=self.tmpdir,
                timeout=1,
                retries=2,
                delay=0,
                headers=self.headers
            )
            # Download should fail and no file created
            self.assertFalse(result)
            self.assertFalse(os.listdir(self.tmpdir))

    def test_check_image_resolution(self):
        # Create a test image with known dimensions
        test_width = 800
        test_height = 600
        test_image = Image.new('RGB', (test_width, test_height), color='red')
        
        # Save to temporary file
        img_path = os.path.join(self.tmpdir, 'test_resolution.jpg')
        test_image.save(img_path)
          # Test meeting requirements
        meets_req, width, height, match_code = check_image_resolution(img_path, 800, 600)
        self.assertTrue(meets_req)
        self.assertEqual(width, test_width)
        self.assertEqual(height, test_height)
        self.assertEqual(match_code, 3)  # Should be exact match
        
        # Test not meeting requirements
        meets_req, width, height, match_code = check_image_resolution(img_path, 1200, 800)
        self.assertFalse(meets_req)
        self.assertEqual(width, test_width)
        self.assertEqual(height, test_height)
        self.assertEqual(match_code, 0)  # Should be unacceptable
    
    def test_download_image_with_resolution_check(self):
        # Create a mock image for the download
        test_image = Image.new('RGB', (100, 100), color='blue')
        img_bytes = io.BytesIO()
        test_image.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        
        # Mock a successful HTTP response with our test image
        mock_resp = Mock(status_code=200, content=img_bytes)
        with patch('wallpaper_scraper.requests.get', return_value=mock_resp):
            # Test with low resolution requirements (should pass)
            result = download_image(
                url=self.test_url,
                output_folder=self.tmpdir,
                timeout=1,
                retries=1,
                delay=0,
                headers=self.headers,
                min_width=50,
                min_height=50
            )
            self.assertTrue(result)
              # Test with high resolution requirements (should fail and return False)
            with patch('wallpaper_scraper.logging.warning') as mock_log:
                result = download_image(
                    url=self.test_url,
                    output_folder=self.tmpdir,
                    timeout=1,
                    retries=1,
                    delay=0,
                    headers=self.headers,
                    min_width=200,
                    min_height=200
                )
                self.assertFalse(result)  # Should return false for insufficient resolution
                self.assertTrue(mock_log.called)  # Check that warning was logged

if __name__ == '__main__':
    unittest.main()
