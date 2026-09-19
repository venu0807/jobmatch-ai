import pytest
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.tailor import tailor_resume, load_master_template, latex_to_plain_text, BANNED_SKILLS_ADVICE

def test_load_master_template():
    tex = load_master_template()
    assert r"\documentclass" in tex
    assert "VENU GOPAL REDDY PALUGULLA" in tex
    assert r"\begin{document}" in tex
    assert r"\end{document}" in tex

def test_latex_to_plain_text():
    sample_tex = r"""
    \section*{TECHNICAL SKILLS}
    \textbf{Backend:} Django, REST APIs. \\
    \item Built an end-to-end ML model.
    """
    plain = latex_to_plain_text(sample_tex)
    assert r"\section" not in plain
    assert r"\textbf" not in plain
    assert "Django" in plain
    assert "REST APIs" in plain
    assert "Built an end-to-end ML model" in plain

def test_tailoring_injects_safe_skills():
    jd = """
    Full Stack Python Developer Opening in Hyderabad:
    Looking for experience with Python, FastAPI, React.js, Tailwind CSS, Docker, and PostgreSQL.
    """
    result = tailor_resume(jd)
    assert result["success"] is True
    assert result["projected_score"] >= result["original_score"]
    
    injected_names = [item["skill"] for item in result["injected_skills"]]
    assert "FastAPI" in injected_names or "Tailwind CSS" in injected_names
    
    tailored_tex = result["tailored_latex"]
    assert "FastAPI" in tailored_tex
    assert r"\begin{document}" in tailored_tex
    assert r"\end{document}" in tailored_tex

def test_anti_hallucination_safeguard_excludes_banned_skills():
    jd = """
    Senior Python Developer:
    Must have extensive production experience with AWS (EC2, S3), Celery, Linux / Ubuntu, and ONNX.
    Also requires Python and Django.
    """
    result = tailor_resume(jd)
    assert result["success"] is True
    
    injected_names = [item["skill"] for item in result["injected_skills"]]
    assert "AWS" not in injected_names
    assert "Celery" not in injected_names
    assert "Linux" not in injected_names
    assert "ONNX" not in injected_names
    
    omitted_names = [item["skill"] for item in result["omitted_banned_skills"]]
    assert "AWS" in omitted_names or "Celery" in omitted_names
    
    # Ensure tailored LaTeX does not falsely claim AWS or Celery in TECHNICAL SKILLS
    tech_skills_section = result["tailored_latex"]
    backend_line = [l for l in tech_skills_section.split("\n") if r"\textbf{Backend:}" in l]
    if backend_line:
        assert "Celery" not in backend_line[0]

def test_score_projection_math():
    jd = """
    Python Developer: Python, Django, DRF, React.js, PostgreSQL, Redis, Docker, PyTest.
    """
    result = tailor_resume(jd)
    assert result["projected_score"] >= 70.0
    assert "ATS Score" in result["formula_breakdown"]

def test_generate_tailored_pdf(tmp_path):
    from core.pdf_compiler import generate_tailored_pdf
    from pypdf import PdfReader
    
    injected = [
        {"skill": "FastAPI", "target_section": "Backend:"},
        {"skill": "Tailwind CSS", "target_section": "Frontend:"}
    ]
    jd = "Python Full Stack Developer: FastAPI, React.js, Tailwind CSS, PostgreSQL."
    out_pdf = tmp_path / "tailored_test.pdf"
    
    success = generate_tailored_pdf(injected, jd, str(out_pdf))
    assert success is True
    assert out_pdf.exists()
    assert out_pdf.stat().st_size > 0
    
    # Verify exact single page
    reader = PdfReader(str(out_pdf))
    assert len(reader.pages) == 1
    
    # Verify keywords are present in extracted text layer
    text = reader.pages[0].extract_text()
    assert "FastAPI" in text
    assert "Tailwind CSS" in text
