import subprocess
import sys
import os

CLI_PATH = os.path.join(os.path.dirname(__file__), '..', 'main.py')


def test_cli_help():
    result = subprocess.run(
        [sys.executable, CLI_PATH, '--help'], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Wallpaper Scraper CLI" in result.stdout
    assert "--scrape" in result.stdout


def test_cli_version():
    result = subprocess.run(
        [sys.executable, CLI_PATH, '--version'], capture_output=True, text=True)
    assert result.returncode == 0
    assert "WallpaperScraper 1.0" in result.stdout


def test_cli_theme_overrides_config():
    # Run CLI with --theme and check output for correct theme usage
    result = subprocess.run([
        sys.executable, CLI_PATH, '--theme', 'testtheme', '--scrape', '--log-level', 'INFO'
    ], capture_output=True, text=True)
    assert result.returncode == 0 or result.returncode == 1  # 1 if no network, 0 if success
    assert 'Themes: testtheme' in result.stdout or 'Themes: testtheme' in result.stderr


def test_cli_resolution_overrides_config():
    result = subprocess.run([
        sys.executable, CLI_PATH, '--theme', 'testtheme', '--resolution', '1234x5678', '--scrape', '--log-level', 'INFO'
    ], capture_output=True, text=True)
    assert result.returncode == 0 or result.returncode == 1
    # Accept log lines with timestamp and log level prefix
    assert any('Starting wallpaper scraper with resolution 1234x5678' in line for line in (result.stdout + result.stderr).splitlines())
