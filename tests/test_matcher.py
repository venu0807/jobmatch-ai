import pytest
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.taxonomy import extract_skills_from_text
from core.matcher import match_resume_to_jd
from core.predictor import predict_interview_questions
from core.analyzer import generate_tailoring_recommendations

def test_extract_skills_from_text():
    sample_text = "We are seeking a Python developer with Django, React.js, PostgreSQL, and Docker experience."
    result = extract_skills_from_text(sample_text)
    skills = result["found_skills"]
    assert "Python" in skills
    assert "Django" in skills
    assert "React.js" in skills
    assert "PostgreSQL" in skills
    assert "Docker" in skills
    assert "Java" not in skills

def test_match_resume_to_jd_high_overlap():
    resume_text = """
    Python Full Stack Developer with experience in Django, Django REST Framework, React.js, PostgreSQL, Redis, Docker.
    Built recommendation systems with Scikit-learn and audio classification with TensorFlow.
    """
    jd_text = """
    Looking for a Python Developer. Must have Django, PostgreSQL, and Docker experience.
    """
    result = match_resume_to_jd(resume_text, jd_text)
    assert result["ats_score"] >= 75.0
    assert "Python" in result["matched_skills"]
    assert "Django" in result["matched_skills"]
    assert "PostgreSQL" in result["matched_skills"]
    assert "Docker" in result["matched_skills"]

def test_predict_interview_questions():
    matched = ["Django", "PostgreSQL", "Python"]
    missing = ["FastAPI", "AWS"]
    questions = predict_interview_questions(matched, missing)
    assert len(questions) == 5
    # Should contain questions for the top skills
    skills_in_q = [q["skill"] for q in questions]
    assert "Django" in skills_in_q or "Python" in skills_in_q

def test_generate_tailoring_recommendations():
    missing = ["FastAPI", "AWS"]
    matched = ["Django", "PostgreSQL"]
    tips = generate_tailoring_recommendations(missing, matched, "FastAPI AWS")
    assert len(tips) >= 2
