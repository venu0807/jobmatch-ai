import os
import json
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
EXT_DIR = BASE_DIR / "extension"

def test_manifest_structure():
    manifest_file = EXT_DIR / "manifest.json"
    assert manifest_file.exists()
    
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    assert manifest["manifest_version"] == 3
    assert "JobMatch AI" in manifest["name"]
    assert "sidePanel" in manifest["permissions"]
    assert "activeTab" in manifest["permissions"]
    assert "scripting" in manifest["permissions"]
    assert "downloads" in manifest["permissions"]
    assert manifest["side_panel"]["default_path"] == "sidepanel.html"
    assert manifest["background"]["service_worker"] == "service-worker.js"

def test_icons_integrity():
    manifest_file = EXT_DIR / "manifest.json"
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    for size_str, rel_path in manifest["icons"].items():
        icon_path = EXT_DIR / rel_path
        assert icon_path.exists()
        img = Image.open(icon_path)
        expected = int(size_str)
        assert img.size == (expected, expected)
        assert img.format == "PNG"

def test_content_scraper_selectors():
    scraper_file = EXT_DIR / "content-scraper.js"
    assert scraper_file.exists()
    
    with open(scraper_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    assert "linkedin.com" in content
    assert "naukri.com" in content
    assert "indeed.com" in content
    assert "jobs-description" in content
    assert "job-desc" in content
