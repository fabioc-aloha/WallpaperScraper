"""
Enhanced error handling and logging utilities for WallpaperScraper.
Provides custom exceptions, retry decorators, and structured logging.
"""

import logging
import functools
import time
import sys
import traceback
from typing import Optional, Callable, Any, Type
from pathlib import Path


class WallpaperScraperError(Exception):
    """Base exception for WallpaperScraper errors."""
    pass


class NetworkError(WallpaperScraperError):
    """Network-related errors (timeouts, connection issues, etc.)."""
    pass


class ResolutionError(WallpaperScraperError):
    """Resolution validation errors."""
    pass


class ServiceError(WallpaperScraperError):
    """Service-specific errors (site parsing, API issues, etc.)."""
    pass


class ConfigurationError(WallpaperScraperError):
    """Configuration validation errors."""
    pass


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorator to retry function execution on specified exceptions.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exception types to retry on
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_retries:
                        logging.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                        raise
                    
                    logging.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff_factor
            
            raise last_exception
        return wrapper
    return decorator


def log_execution_time(func: Callable) -> Callable:
    """Decorator to log function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logging.debug(f"{func.__name__} completed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(f"{func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    return wrapper


def setup_enhanced_logging(
    log_level: str = 'INFO',
    log_file: Optional[Path] = None,
    include_debug: bool = False
) -> None:
    """
    Set up enhanced logging with file and console handlers.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging
        include_debug: Whether to include debug information in logs
    """
    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(simple_formatter if not include_debug else detailed_formatter)
    
    # File handler (if specified)
    handlers = [console_handler]
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # Always debug level for files
        file_handler.setFormatter(detailed_formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.DEBUG,  # Set to DEBUG, handlers control what gets output
        handlers=handlers,
        force=True
    )


def log_unhandled_exception(exc_type: Type, exc_value: Exception, exc_traceback) -> None:
    """Log unhandled exceptions with full traceback."""
    if issubclass(exc_type, KeyboardInterrupt):
        # Don't log keyboard interrupts
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logging.critical(
        "Unhandled exception occurred",
        exc_info=(exc_type, exc_value, exc_traceback)
    )


def validate_resolution(resolution: str) -> tuple[int, int]:
    """
    Validate and parse resolution string.
    
    Args:
        resolution: Resolution string in format 'WIDTHxHEIGHT'
        
    Returns:
        Tuple of (width, height) as integers
        
    Raises:
        ResolutionError: If resolution format is invalid
    """
    try:
        width_str, height_str = resolution.lower().split('x')
        width, height = int(width_str), int(height_str)
        
        if width <= 0 or height <= 0:
            raise ResolutionError(f"Resolution dimensions must be positive: {resolution}")
        
        if width < 800 or height < 600:
            logging.warning(f"Resolution {resolution} is quite small, results may be limited")
        
        return width, height
    except ValueError:
        raise ResolutionError(f"Invalid resolution format '{resolution}'. Expected format: 'WIDTHxHEIGHT' (e.g., '1920x1080')")


def safe_filename(filename: str, max_length: int = 255) -> str:
    """
    Create a safe filename by removing/replacing problematic characters.
    
    Args:
        filename: Original filename
        max_length: Maximum allowed filename length
        
    Returns:
        Sanitized filename
    """
    # Replace problematic characters
    unsafe_chars = '<>:"/\\|?*'
    safe_name = filename
    
    for char in unsafe_chars:
        safe_name = safe_name.replace(char, '_')
    
    # Remove control characters
    safe_name = ''.join(char for char in safe_name if ord(char) >= 32)
    
    # Trim length
    if len(safe_name) > max_length:
        name, ext = Path(safe_name).stem, Path(safe_name).suffix
        max_name_length = max_length - len(ext)
        safe_name = name[:max_name_length] + ext
    
    return safe_name.strip()


# Set up global exception handler
sys.excepthook = log_unhandled_exception
