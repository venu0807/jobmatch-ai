import os
import re
import shutil
import tempfile
import subprocess
from pathlib import Path
from .taxonomy import TECH_TAXONOMY

def find_headless_browser() -> str:
    """
    Locates Google Chrome, Microsoft Edge, or Chromium executable for Windows and Linux/Docker headless PDF rendering.
    """
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable"
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
            
    # Try PATH resolution
    browser_path = (
        shutil.which("chromium")
        or shutil.which("chromium-browser")
        or shutil.which("google-chrome")
        or shutil.which("google-chrome-stable")
        or shutil.which("chrome")
        or shutil.which("msedge")
        or shutil.which("edge")
    )
    if browser_path:
        return browser_path

    return None

def load_html_template() -> str:
    base_dir = Path(__file__).resolve().parent
    template_path = base_dir / "resume_template.html"
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

def tailor_html_resume(injected_skills: list, jd_text: str) -> str:
    """
    Injects tailored keywords into core/resume_template.html while preserving single-page layout.
    """
    html = load_html_template()
    jd_lower = jd_text.lower()
    
    # Group injected skills by category
    by_category = {
        "Languages & Backend": [],
        "Frontend Development": [],
        "Databases & Caching": [],
        "Machine Learning & AI": [],
        "DevOps, Quality & CS": []
    }
    
    for item in injected_skills:
        skill = item["skill"] if isinstance(item, dict) else str(item)
        target = item.get("target_section", "") if isinstance(item, dict) else ""
        
        if "backend" in target.lower() or "languages" in target.lower():
            by_category["Languages & Backend"].append(skill)
        elif "frontend" in target.lower():
            by_category["Frontend Development"].append(skill)
        elif "database" in target.lower():
            by_category["Databases & Caching"].append(skill)
        elif "machine learning" in target.lower():
            by_category["Machine Learning & AI"].append(skill)
        else:
            by_category["DevOps, Quality & CS"].append(skill)

    # Injections into HTML lines
    category_id_map = {
        "Languages & Backend": ('id="skill-languages"', 'Languages &amp; Backend:</span>'),
        "Frontend Development": ('id="skill-frontend"', 'Frontend Development:</span>'),
        "Databases & Caching": ('id="skill-databases"', 'Databases &amp; Caching:</span>'),
        "Machine Learning & AI": ('id="skill-ml"', 'Machine Learning &amp; AI:</span>'),
        "DevOps, Quality & CS": ('id="skill-devops"', 'DevOps, Quality &amp; CS:</span>')
    }

    for cat_name, skills in by_category.items():
        if not skills:
            continue
        marker, label = category_id_map[cat_name]
        if marker in html:
            # Extract current line content
            pattern = re.escape(label) + r"(.*?)</div>"
            match = re.search(pattern, html)
            if match:
                current_text = match.group(1).strip()
                skills_to_add = [s for s in skills if s.lower() not in current_text.lower()]
                if skills_to_add:
                    addition = ", " + ", ".join(skills_to_add)
                    new_text = f"{label} {current_text}{addition}</div>"
                    html = html.replace(match.group(0), new_text, 1)

    # Project bullet refinements
    if "fastapi" in jd_lower and "fastapi" not in html.lower():
        html = html.replace(
            "Django REST Framework backend and React.js frontend.",
            "Django REST Framework and FastAPI backend with React.js frontend."
        )

    if ("pytest" in jd_lower or "unit test" in jd_lower) and "pytest" not in html.lower():
        html = html.replace(
            "Engineered background daemon processes",
            "Engineered background daemons and automated PyTest verification suites"
        )

    return html

def compile_html_to_pdf(html_content: str, output_pdf_path: str) -> bool:
    """
    Compiles HTML to a crisp A4 vector PDF using Windows headless browser.
    """
    browser = find_headless_browser()
    if not browser:
        print("[PDF Compiler] No Chrome or Edge browser found.")
        return False

    abs_pdf = os.path.abspath(output_pdf_path)
    os.makedirs(os.path.dirname(abs_pdf), exist_ok=True)

    temp_dir = tempfile.mkdtemp(prefix="jobmatch_pdf_")
    temp_html = os.path.join(temp_dir, "resume.html")

    try:
        with open(temp_html, "w", encoding="utf-8") as f:
            f.write(html_content)

        abs_html = os.path.abspath(temp_html)
        abs_pdf = os.path.abspath(output_pdf_path)

        # Chrome/Edge flags for exact single-page print
        cmd = [
            browser,
            "--headless=new",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={abs_pdf}",
            abs_html
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        success = os.path.exists(abs_pdf) and os.path.getsize(abs_pdf) > 0
        return success
    except Exception as e:
        print(f"[PDF Compiler] Compilation error: {e}")
        return False
    finally:
        try:
            shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass

def generate_tailored_pdf(injected_skills: list, jd_text: str, output_pdf_path: str) -> bool:
    """
    One-step helper: Takes injected skills + JD -> generates tailored PDF at output_pdf_path.
    """
    tailored_html = tailor_html_resume(injected_skills, jd_text)
    return compile_html_to_pdf(tailored_html, output_pdf_path)
