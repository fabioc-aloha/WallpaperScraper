import unittest
from unittest.mock import patch, Mock
from services.fourk_wallpapers_service import FourKWallpapersService

class TestFourKWallpapersService(unittest.TestCase):
    def test_fetch_wallpapers_no_tiles(self):
        # Simulate a search page with no wallpaper tiles
        html = '<html><body>No wallpapers here</body></html>'
        mock_resp = Mock(status_code=200, text=html)
        # Patch requests.get for both search and detail requests
        with patch('services.fourk_wallpapers_service.requests.get', return_value=mock_resp):
            service = FourKWallpapersService(resolution="5120x1440", themes=["nature"])
            result = service.fetch_wallpapers()
            self.assertEqual(result, [])

if __name__ == '__main__':
    unittest.main()
