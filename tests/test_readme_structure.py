import re
import pytest

README_PATH = "README.md"


@pytest.fixture
def readme_text():
    with open(README_PATH, encoding="utf-8") as f:
        return f.read()


def test_banner_at_top(readme_text):
    assert readme_text.lstrip().startswith(
        "![WallpaperScraper Banner](banner.png)"), "Banner image must be at the very top of README.md."


def test_abstract_after_banner(readme_text):
    # Abstract should be within the first 20 lines after the banner
    lines = readme_text.splitlines()
    banner_idx = next(
        (i for i, l in enumerate(lines) if "banner.png" in l), -1)
    abstract_idx = next((i for i, l in enumerate(
        lines) if l.strip().lower() == "### abstract"), -1)
    assert banner_idx != -1 and abstract_idx != - \
        1, "Banner and abstract must both be present."
    assert 0 < abstract_idx - \
        banner_idx <= 3, "Abstract section should immediately follow the banner."


def test_project_structure_section(readme_text):
    assert "Project Structure Update" in readme_text, "Project structure update section missing."
    assert "src/" in readme_text, "src/ folder reference missing."
    assert "main.py" in readme_text, "main.py reference missing."


def test_usage_instructions(readme_text):
    assert "python main.py --scrape" in readme_text, "Usage instructions for running the CLI are missing or incorrect."


def test_paper_link(readme_text):
    assert re.search(r"\[.*PAPER.md.*\]\(PAPER.md\)",
                     readme_text), "Link to PAPER.md missing."
