"""
Test enhanced CLI functionality and new features.
"""
import subprocess
import sys
import os
import tempfile
import pytest
from pathlib import Path

CLI_PATH = os.path.join(os.path.dirname(__file__), '..', 'main.py')


class TestEnhancedCLI:
    """Test enhanced CLI features."""
    
    def test_cli_help_shows_examples(self):
        """Test that help includes usage examples."""
        result = subprocess.run(
            [sys.executable, CLI_PATH, '--help'], 
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "Examples:" in result.stdout
        assert "--scout" in result.stdout
        assert "--investigate" in result.stdout
    
    def test_cli_version_updated(self):
        """Test that version shows updated version number."""
        result = subprocess.run(
            [sys.executable, CLI_PATH, '--version'], 
            capture_output=True, text=True
        )
        assert result.returncode == 0
        assert "1.0.2" in result.stdout
    
    def test_cli_scout_option(self):
        """Test that scout option is available."""
        result = subprocess.run(
            [sys.executable, CLI_PATH, '--scout'], 
            capture_output=True, text=True, timeout=30
        )
        # Should not error immediately (may timeout due to network)
        assert result.returncode in [0, 1]  # 0 for success, 1 for network issues
    
    def test_cli_dry_run_option(self):
        """Test dry run functionality."""
        result = subprocess.run([
            sys.executable, CLI_PATH, 
            '--scrape', '--theme', 'nature', 
            '--dry-run', '--log-level', 'INFO'
        ], capture_output=True, text=True, timeout=60)
        
        # Should succeed and show dry run message
        assert result.returncode in [0, 1]
        output = result.stdout + result.stderr
        assert 'DRY RUN' in output or 'dry run' in output.lower()
    
    def test_cli_max_downloads_option(self):
        """Test max downloads option."""
        result = subprocess.run([
            sys.executable, CLI_PATH, 
            '--scrape', '--theme', 'test', 
            '--max-downloads', '5',
            '--dry-run', '--log-level', 'INFO'
        ], capture_output=True, text=True, timeout=60)
        
        assert result.returncode in [0, 1]
        # Option should be parsed without error
    
    def test_cli_output_directory_option(self):
        """Test custom output directory option."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = subprocess.run([
                sys.executable, CLI_PATH, 
                '--scrape', '--theme', 'test', 
                '--output', temp_dir,
                '--dry-run', '--log-level', 'INFO'
            ], capture_output=True, text=True, timeout=60)
            
            assert result.returncode in [0, 1]
    
    def test_cli_workers_option(self):
        """Test workers option."""
        result = subprocess.run([
            sys.executable, CLI_PATH, 
            '--scrape', '--theme', 'test', 
            '--workers', '2',
            '--dry-run', '--log-level', 'INFO'
        ], capture_output=True, text=True, timeout=60)
        
        assert result.returncode in [0, 1]
    
    def test_cli_timeout_option(self):
        """Test timeout option."""
        result = subprocess.run([
            sys.executable, CLI_PATH, 
            '--scrape', '--theme', 'test', 
            '--timeout', '15',
            '--dry-run', '--log-level', 'INFO'
        ], capture_output=True, text=True, timeout=60)
        
        assert result.returncode in [0, 1]
    
    def test_cli_verbose_option(self):
        """Test verbose logging option."""
        result = subprocess.run([
            sys.executable, CLI_PATH, 
            '--scrape', '--theme', 'test', 
            '--verbose', '--dry-run'
        ], capture_output=True, text=True, timeout=60)
        
        assert result.returncode in [0, 1]
    
    def test_cli_sites_option(self):
        """Test sites selection option."""
        result = subprocess.run([
            sys.executable, CLI_PATH, 
            '--scrape', '--theme', 'test', 
            '--sites', 'wallhaven.cc',
            '--dry-run', '--log-level', 'INFO'
        ], capture_output=True, text=True, timeout=60)
        
        assert result.returncode in [0, 1]
    
    def test_cli_investigate_option(self):
        """Test investigate option."""
        result = subprocess.run([
            sys.executable, CLI_PATH, 
            '--investigate', 'wallpaperswide.com'
        ], capture_output=True, text=True, timeout=30)
        
        # Should not error immediately
        assert result.returncode in [0, 1]
    
    def test_cli_mutually_exclusive_actions(self):
        """Test that main actions are mutually exclusive."""
        result = subprocess.run([
            sys.executable, CLI_PATH, 
            '--scrape', '--scout'
        ], capture_output=True, text=True)
        
        # Should show error for mutually exclusive options
        assert result.returncode == 2
        assert "not allowed" in result.stderr.lower()


class TestCLIErrorHandling:
    """Test CLI error handling."""
    
    def test_invalid_log_level(self):
        """Test handling of invalid log level."""
        result = subprocess.run([
            sys.executable, CLI_PATH, 
            '--scrape', '--theme', 'test',
            '--log-level', 'INVALID'
        ], capture_output=True, text=True)
        
        # Should show error for invalid choice
        assert result.returncode == 2
        assert "invalid choice" in result.stderr.lower()
    
    def test_invalid_sites_option(self):
        """Test handling of invalid sites."""
        result = subprocess.run([
            sys.executable, CLI_PATH, 
            '--scrape', '--theme', 'test',
            '--sites', 'invalid.site.com'
        ], capture_output=True, text=True)
        
        # Should show error for invalid choice
        assert result.returncode == 2
        assert "invalid choice" in result.stderr.lower()
    
    def test_no_action_specified(self):
        """Test that help is shown when no action is specified."""
        result = subprocess.run([
            sys.executable, CLI_PATH
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert "usage:" in result.stdout.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
