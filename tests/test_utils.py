"""
Test enhanced error handling and utility functions.
"""
import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, Mock
from src.utils import (
    retry_on_exception, log_execution_time, validate_resolution,
    safe_filename, NetworkError, ServiceError, ResolutionError
)


class TestCustomExceptions:
    """Test custom exception classes."""
    
    def test_network_error_inheritance(self):
        """Test that NetworkError inherits from WallpaperScraperError."""
        from src.utils import WallpaperScraperError
        error = NetworkError("Test network error")
        assert isinstance(error, WallpaperScraperError)
        assert str(error) == "Test network error"
    
    def test_service_error_inheritance(self):
        """Test that ServiceError inherits from WallpaperScraperError."""
        from src.utils import WallpaperScraperError
        error = ServiceError("Test service error")
        assert isinstance(error, WallpaperScraperError)
        assert str(error) == "Test service error"
    
    def test_resolution_error_inheritance(self):
        """Test that ResolutionError inherits from WallpaperScraperError."""
        from src.utils import WallpaperScraperError
        error = ResolutionError("Test resolution error")
        assert isinstance(error, WallpaperScraperError)
        assert str(error) == "Test resolution error"


class TestRetryDecorator:
    """Test the retry_on_exception decorator."""
    
    def test_retry_success_on_first_attempt(self):
        """Test that function succeeds on first attempt."""
        call_count = 0
        
        @retry_on_exception(max_retries=3, delay=0.01)
        def test_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = test_function()
        assert result == "success"
        assert call_count == 1
    
    def test_retry_success_after_failures(self):
        """Test that function succeeds after some failures."""
        call_count = 0
        
        @retry_on_exception(max_retries=3, delay=0.01)
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = test_function()
        assert result == "success"
        assert call_count == 3
    
    def test_retry_max_retries_exceeded(self):
        """Test that function fails after max retries."""
        call_count = 0
        
        @retry_on_exception(max_retries=2, delay=0.01, exceptions=(ValueError,))
        def test_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Persistent failure")
        
        with pytest.raises(ValueError, match="Persistent failure"):
            test_function()
        
        assert call_count == 3  # Initial call + 2 retries
    
    def test_retry_only_specified_exceptions(self):
        """Test that retry only occurs for specified exceptions."""
        call_count = 0
        
        @retry_on_exception(max_retries=3, delay=0.01, exceptions=(ValueError,))
        def test_function():
            nonlocal call_count
            call_count += 1
            raise TypeError("Different exception")
        
        with pytest.raises(TypeError, match="Different exception"):
            test_function()
        
        assert call_count == 1  # No retries for TypeError


class TestLogExecutionTime:
    """Test the log_execution_time decorator."""
    
    def test_log_execution_time_success(self, caplog):
        """Test that execution time is logged for successful function."""
        import logging
        caplog.set_level(logging.DEBUG)  # Ensure we capture debug logs
        
        @log_execution_time
        def test_function():
            time.sleep(0.01)
            return "result"
        
        result = test_function()
        assert result == "result"
        
        # Check that execution time was logged
        log_messages = [record.message for record in caplog.records]
        execution_time_logged = any("completed in" in msg for msg in log_messages)
        assert execution_time_logged
    
    def test_log_execution_time_failure(self, caplog):
        """Test that execution time is logged for failed function."""
        @log_execution_time
        def test_function():
            time.sleep(0.01)
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            test_function()
        
        # Check that execution time was logged with failure
        log_messages = [record.message for record in caplog.records]
        failure_time_logged = any("failed after" in msg for msg in log_messages)
        assert failure_time_logged


class TestResolutionValidation:
    """Test resolution validation function."""
    
    def test_valid_resolution_parsing(self):
        """Test parsing valid resolution strings."""
        width, height = validate_resolution("1920x1080")
        assert width == 1920
        assert height == 1080
        
        width, height = validate_resolution("5120X1440")  # Test case insensitive
        assert width == 5120
        assert height == 1440
    
    def test_invalid_resolution_format(self):
        """Test handling invalid resolution formats."""
        with pytest.raises(ResolutionError, match="Invalid resolution format"):
            validate_resolution("1920")
        
        with pytest.raises(ResolutionError, match="Invalid resolution format"):
            validate_resolution("1920x")
        
        with pytest.raises(ResolutionError, match="Invalid resolution format"):
            validate_resolution("not_a_resolution")
    
    def test_negative_resolution_values(self):
        """Test handling negative resolution values."""
        with pytest.raises(ResolutionError, match="must be positive"):
            validate_resolution("-1920x1080")
        
        with pytest.raises(ResolutionError, match="must be positive"):
            validate_resolution("1920x-1080")
    
    def test_zero_resolution_values(self):
        """Test handling zero resolution values."""
        with pytest.raises(ResolutionError, match="must be positive"):
            validate_resolution("0x1080")
        
        with pytest.raises(ResolutionError, match="must be positive"):
            validate_resolution("1920x0")
    
    def test_small_resolution_warning(self, caplog):
        """Test that warning is logged for small resolutions."""
        width, height = validate_resolution("640x480")
        assert width == 640
        assert height == 480
        
        # Check that warning was logged
        warning_logged = any("quite small" in record.message for record in caplog.records)
        assert warning_logged


class TestSafeFilename:
    """Test safe filename generation."""
    
    def test_removes_unsafe_characters(self):
        """Test that unsafe characters are replaced."""
        unsafe_name = "file<>:\"/\\|?*.jpg"
        safe_name = safe_filename(unsafe_name)
        
        unsafe_chars = '<>:"/\\|?*'
        for char in unsafe_chars:
            assert char not in safe_name
    
    def test_preserves_safe_characters(self):
        """Test that safe characters are preserved."""
        safe_name_input = "nature_wallpaper-2024.jpg"
        result = safe_filename(safe_name_input)
        assert result == safe_name_input
    
    def test_removes_control_characters(self):
        """Test that control characters are removed."""
        name_with_control = "file\x00\x01\x02.jpg"
        result = safe_filename(name_with_control)
        assert result == "file.jpg"
    
    def test_length_limiting(self):
        """Test that long filenames are trimmed."""
        long_name = "a" * 300 + ".jpg"
        result = safe_filename(long_name, max_length=100)
        
        assert len(result) <= 100
        assert result.endswith(".jpg")  # Extension should be preserved
    
    def test_empty_filename(self):
        """Test handling of empty filename."""
        result = safe_filename("")
        assert result == ""
    
    def test_whitespace_trimming(self):
        """Test that leading/trailing whitespace is trimmed."""
        result = safe_filename("  filename.jpg  ")
        assert result == "filename.jpg"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
