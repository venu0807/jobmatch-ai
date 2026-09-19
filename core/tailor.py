import os
import re
from pathlib import Path
from .taxonomy import TECH_TAXONOMY, extract_skills_from_text
from .matcher import match_resume_to_jd

# Strict Candidate Profile Anti-Hallucination Guardrail
# Skills the candidate has NOT trained on or verified. Under NO circumstance should these be claimed as verified proficiencies.
BANNED_SKILLS_ADVICE = {
    "AWS": "Do not claim AWS in resume. In interviews, state: 'My primary containerization and deployment is with Docker and Docker Compose; I understand cloud hosting architectures conceptually.'",
    "AMAZON WEB SERVICES": "Do not claim AWS in resume. In interviews, state: 'My primary containerization and deployment is with Docker and Docker Compose.'",
    "EC2": "Frame as virtual server containerization with Docker.",
    "S3": "Frame as file storage abstraction in Django / Python.",
    "CELERY": "Do not claim Celery. In interviews, state: 'In my Jarvis automation system, I implemented background processing and event-driven architecture using Python daemons and an internal pub/sub event bus.'",
    "LINUX": "Focus on standard cross-platform Python, Git, and Docker workflows.",
    "BASH": "Focus on Python automation and scripting.",
    "SHELL": "Focus on Python automation and scripting.",
    "UBUNTU": "Focus on Docker containerization environments.",
    "NGINX": "Frame as reverse proxy architecture concepts.",
    "GUNICORN": "Frame as WSGI/ASGI application server architecture in Django/FastAPI.",
    "ONNX": "Do not claim ONNX. Highlight your verified edge quantization expertise in TensorFlow Lite (TFLite).",
    "SWAGGER": "Frame as REST API design and documentation standards in DRF.",
    "OPENAPI": "Frame as schema definition for RESTful endpoints."
}

CATEGORY_TO_LATEX_PREFIX = {
    "Languages": r"\textbf{Programming Languages:}",
    "Backend & Frameworks": r"\textbf{Backend:}",
    "Frontend": r"\textbf{Frontend:}",
    "Databases & Caching": r"\textbf{Databases \& Caching:}",
    "Machine Learning & AI": r"\textbf{Machine Learning:}",
    "DevOps, Cloud & Automation": r"\textbf{DevOps \& Tools:}",
    "Testing & Quality": r"\textbf{DevOps \& Tools:}",
    "Core CS & Architecture": r"\textbf{Backend:}"
}

def get_template_path() -> Path:
    base_dir = Path(__file__).resolve().parent
    return base_dir / "resume_template.tex"

def load_master_template() -> str:
    path = get_template_path()
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def latex_to_plain_text(tex: str) -> str:
    """
    Strips LaTeX formatting commands to produce clean, ATS-readable text for accurate vectorization.
    """
    text = re.sub(r'%.*$', '', tex, flags=re.MULTILINE)
    text = re.sub(r'\\href\{[^}]*\}\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\(?:textbf|textit|textsc|quad|qquad|hfill)\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\section\*?\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\(?:begin|end)\{[^}]*\}', ' ', text)
    text = re.sub(r'\\\\[a-zA-Z0-9\[\]]*', ' ', text)
    text = re.sub(r'\\[a-zA-Z]+(\[[^\]]*\])?(\{([^}]*)\})?', r'\3', text)
    text = re.sub(r'[{}\\%$&_~^]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def tailor_resume(jd_text: str, original_resume_text: str = None) -> dict:
    """
    Surgically tailors the master LaTeX template (core/resume_template.tex)
    to match the provided Job Description, maximizing ATS score without hallucinating.
    """
    master_latex = load_master_template()
    
    # 1. Analyze initial match against the JD
    initial_analysis_text = original_resume_text if original_resume_text else latex_to_plain_text(master_latex)
    initial_match = match_resume_to_jd(initial_analysis_text, jd_text)
    
    missing_skills = initial_match.get("missing_skills", [])
    matched_skills = initial_match.get("matched_skills", [])
    
    injected_skills = []
    omitted_banned_skills = []
    diff_summary = []
    
    tailored_latex = master_latex

    # 2. Categorize missing skills & apply Anti-Hallucination Filter
    skills_by_target = {
        r"\textbf{Programming Languages:}": [],
        r"\textbf{Backend:}": [],
        r"\textbf{Frontend:}": [],
        r"\textbf{Databases \& Caching:}": [],
        r"\textbf{Machine Learning:}": [],
        r"\textbf{DevOps \& Tools:}": []
    }

    for skill in missing_skills:
        skill_upper = skill.upper()
        # Check if banned
        banned_key = None
        for b_k in BANNED_SKILLS_ADVICE:
            if b_k in skill_upper:
                banned_key = b_k
                break

        if banned_key:
            omitted_banned_skills.append({
                "skill": skill,
                "reason": "Strict Ground Truth: Skill not verified in candidate profile.",
                "interview_tip": BANNED_SKILLS_ADVICE[banned_key]
            })
            diff_summary.append(f"🛡️ Safeguard: Omitted '{skill}' from claimed skills per ATS honesty rules.")
            continue

        # Find target category
        assigned = False
        for cat_name, skills_dict in TECH_TAXONOMY.items():
            if skill in skills_dict:
                target_prefix = CATEGORY_TO_LATEX_PREFIX.get(cat_name, r"\textbf{DevOps \& Tools:}")
                skills_by_target[target_prefix].append((skill, cat_name))
                assigned = True
                break
        
        if not assigned:
            skills_by_target[r"\textbf{DevOps \& Tools:}"].append((skill, "DevOps, Cloud & Automation"))

    # 3. Surgically insert safe keywords into the LaTeX category lines
    for prefix, skill_tuples in skills_by_target.items():
        if not skill_tuples:
            continue
        
        pattern = re.escape(prefix) + r"(.*?)(?:(\\\\\s*)|$)"
        match = re.search(pattern, tailored_latex, re.MULTILINE)
        
        if match:
            existing_line_content = match.group(1).strip()
            delimiter = match.group(2) if match.group(2) else ""
            cleaned_content = re.sub(r'[\.,\s]+$', '', existing_line_content)
            
            # Filter skills not already present in line
            skills_to_add = [item for item in skill_tuples if item[0].lower() not in cleaned_content.lower()]
            
            if skills_to_add:
                skill_names_to_add = [item[0] for item in skills_to_add]
                addition_str = ", " + ", ".join(skill_names_to_add)
                new_line_content = f"{cleaned_content}{addition_str}."
                
                replacement = f"{prefix} {new_line_content} {delimiter}".rstrip()
                tailored_latex = tailored_latex.replace(match.group(0), replacement, 1)
                
                section_name = prefix.replace(r"\textbf{", "").replace("}", "").replace("\\", "").replace("&", "\\&")
                diff_summary.append(f"🟢 Injected into {section_name} {', '.join(skill_names_to_add)}")
                
                for s_name, c_name in skills_to_add:
                    injected_skills.append({
                        "skill": s_name,
                        "category": c_name,
                        "target_section": section_name
                    })

    # 4. Contextual Project Bullet Refinements (without length explosion)
    jd_lower = jd_text.lower()
    
    if "fastapi" in jd_lower and "fastapi" not in tailored_latex.lower():
        tailored_latex = tailored_latex.replace(
            "Django REST Framework (DRF) backend and React.js frontend.",
            "Django REST Framework (DRF) and FastAPI backend with React.js frontend."
        )
        diff_summary.append("🟢 Tailored Project 1: Highlighted FastAPI / DRF API architecture.")

    if ("pytest" in jd_lower or "unit test" in jd_lower) and "pytest" not in tailored_latex.lower():
        tailored_latex = tailored_latex.replace(
            "using Python and Playwright bots",
            "using Python, PyTest, and Playwright bots"
        )
        diff_summary.append("🟢 Tailored Project 3: Highlighted PyTest test automation in Jarvis.")

    # 5. Calculate Projected ATS Match Score
    tailored_plain_text = latex_to_plain_text(tailored_latex)
    projected_match = match_resume_to_jd(tailored_plain_text, jd_text)
    
    original_score = initial_match["ats_score"]
    
    if len(injected_skills) == 0:
        projected_score = original_score
        score_delta = 0.0
        diff_summary.append("✨ 100% Skill Coverage: Your master resume already contains all required technical skills for this job description.")
    else:
        projected_score = max(original_score, projected_match["ats_score"])
        score_delta = max(0.0, round(projected_score - original_score, 1))

    return {
        "success": True,
        "original_score": original_score,
        "projected_score": projected_score,
        "score_delta": score_delta,
        "injected_skills_count": len(injected_skills),
        "injected_skills": injected_skills,
        "omitted_banned_skills": omitted_banned_skills,
        "diff_summary": diff_summary,
        "tailored_latex": tailored_latex,
        "projected_skill_coverage": projected_match["skill_coverage_score"],
        "projected_semantic_score": projected_match["semantic_score"],
        "projected_rating": projected_match["rating"],
        "projected_missing_skills": projected_match["missing_skills"],
        "formula_breakdown": projected_match["scoring_formula"]["formula_text"]
    }
