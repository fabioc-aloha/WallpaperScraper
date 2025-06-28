import pytest
import subprocess
import sys


def test_multiple_themes():
    """Test CLI with multiple themes."""
    result = subprocess.run([
        sys.executable, 'main.py',
        '--theme', 'nature', 'abstract', 'city',
        '--scrape',
        '--log-level', 'INFO'
    ], capture_output=True, text=True)
    assert result.returncode == 0 or result.returncode == 1  # 1 if no network
    # Check that all themes are processed
    assert 'Themes: nature, abstract, city' in (result.stdout + result.stderr)


def test_multiword_themes():
    """Test CLI with multi-word themes using quotes."""
    result = subprocess.run([
        sys.executable, 'main.py',
        '--theme', 'new york', 'mountain lake',
        '--scrape',
        '--log-level', 'INFO'
    ], capture_output=True, text=True)
    assert result.returncode == 0 or result.returncode == 1  # 1 if no network
    # Check that multi-word themes are processed correctly
    assert 'Themes: new york, mountain lake' in (result.stdout + result.stderr)
