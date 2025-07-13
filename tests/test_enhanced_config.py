"""
Test enhanced configuration and environment variable handling.
"""
import os
import tempfile
import pytest
from unittest.mock import patch
from src.config import CONFIG, get_env_bool, get_env_int, get_env_float, get_env_list


class TestEnvironmentVariables:
    """Test environment variable parsing functions."""
    
    def test_get_env_bool_true_values(self):
        """Test that various true values are parsed correctly."""
        true_values = ['true', 'True', 'TRUE', '1', 'yes', 'on']
        
        for value in true_values:
            with patch.dict(os.environ, {'TEST_BOOL': value}):
                assert get_env_bool('TEST_BOOL') is True
    
    def test_get_env_bool_false_values(self):
        """Test that various false values are parsed correctly."""
        false_values = ['false', 'False', 'FALSE', '0', 'no', 'off', '']
        
        for value in false_values:
            with patch.dict(os.environ, {'TEST_BOOL': value}):
                assert get_env_bool('TEST_BOOL') is False
    
    def test_get_env_bool_default(self):
        """Test that default value is returned when env var doesn't exist."""
        assert get_env_bool('NONEXISTENT_BOOL', True) is True
        assert get_env_bool('NONEXISTENT_BOOL', False) is False
    
    def test_get_env_int_valid(self):
        """Test parsing valid integer values."""
        with patch.dict(os.environ, {'TEST_INT': '42'}):
            assert get_env_int('TEST_INT', 0) == 42
    
    def test_get_env_int_invalid(self):
        """Test handling invalid integer values."""
        with patch.dict(os.environ, {'TEST_INT': 'not_a_number'}):
            assert get_env_int('TEST_INT', 10) == 10  # Should return default
    
    def test_get_env_float_valid(self):
        """Test parsing valid float values."""
        with patch.dict(os.environ, {'TEST_FLOAT': '3.14'}):
            assert get_env_float('TEST_FLOAT', 0.0) == 3.14
    
    def test_get_env_float_invalid(self):
        """Test handling invalid float values."""
        with patch.dict(os.environ, {'TEST_FLOAT': 'not_a_float'}):
            assert get_env_float('TEST_FLOAT', 2.5) == 2.5  # Should return default
    
    def test_get_env_list_valid(self):
        """Test parsing comma-separated list values."""
        with patch.dict(os.environ, {'TEST_LIST': 'item1,item2,item3'}):
            result = get_env_list('TEST_LIST', [])
            assert result == ['item1', 'item2', 'item3']
    
    def test_get_env_list_with_spaces(self):
        """Test parsing list with spaces around items."""
        with patch.dict(os.environ, {'TEST_LIST': ' item1 , item2 , item3 '}):
            result = get_env_list('TEST_LIST', [])
            assert result == ['item1', 'item2', 'item3']
    
    def test_get_env_list_empty(self):
        """Test handling empty list."""
        with patch.dict(os.environ, {'TEST_LIST': ''}):
            result = get_env_list('TEST_LIST', ['default'])
            assert result == ['default']
    
    def test_get_env_list_nonexistent(self):
        """Test default value for nonexistent list."""
        result = get_env_list('NONEXISTENT_LIST', ['default1', 'default2'])
        assert result == ['default1', 'default2']


class TestConfigurationIntegration:
    """Test configuration integration with environment variables."""
    
    def test_config_uses_environment_variables(self):
        """Test that CONFIG uses environment variables when available."""
        with patch.dict(os.environ, {
            'REQUEST_TIMEOUT': '45',
            'MAX_RETRIES': '5',
            'DEBUG': 'true'
        }):
            # Re-import config to pick up new env vars
            import importlib
            from src import config
            importlib.reload(config)
            
            assert config.CONFIG['REQUEST_TIMEOUT'] == 45
            assert config.CONFIG['MAX_RETRIES'] == 5
            assert config.CONFIG['DEBUG'] is True
    
    def test_config_defaults_when_no_env(self):
        """Test that CONFIG uses defaults when no environment variables."""
        # Clear relevant environment variables
        env_vars_to_clear = [
            'REQUEST_TIMEOUT', 'MAX_RETRIES', 'DEBUG', 
            'DEFAULT_DOWNLOAD_DIR', 'MAX_CONCURRENT_DOWNLOADS'
        ]
        
        with patch.dict(os.environ, {}, clear=True):
            for var in env_vars_to_clear:
                os.environ.pop(var, None)
            
            # Re-import config
            import importlib
            from src import config
            importlib.reload(config)
            
            # Should use defaults
            assert isinstance(config.CONFIG['REQUEST_TIMEOUT'], int)
            assert isinstance(config.CONFIG['MAX_RETRIES'], int)
            assert isinstance(config.CONFIG['DEBUG'], bool)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
