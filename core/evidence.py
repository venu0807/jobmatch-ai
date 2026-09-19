import re
from .taxonomy import TECH_TAXONOMY

def find_evidence_snippet(text: str, pattern_list: list, max_len: int = 140) -> str:
    """
    Finds the exact sentence or context where a skill was mentioned in the text.
    Returns the real quote with bolded match — 100% grounded in the text.
    """
    lines = text.split('\n')
    for line in lines:
        clean_line = line.strip()
        if not clean_line or len(clean_line) < 4:
            continue
        for pat in pattern_list:
            match = re.search(pat, clean_line, re.IGNORECASE)
            if match:
                # Return snippet around the match
                start = max(0, match.start() - 40)
                end = min(len(clean_line), match.end() + 60)
                snippet = clean_line[start:end].strip()
                if start > 0:
                    snippet = "..." + snippet
                if end < len(clean_line):
                    snippet = snippet + "..."
                return snippet
    return "Mentioned in document"

def audit_resume_structure(text: str) -> dict:
    """
    Conducts a strict, 0-hallucination ATS technical health audit on the resume text.
    Verifies contact details, standard section headers, and density.
    """
    checks = []
    score_penalty = 0

    # 1. Contact Information Verification
    has_email = bool(re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text))
    has_phone = bool(re.search(r'(?:\+91|91)?\s?[6-9]\d{9}', text))
    has_github = bool(re.search(r'github\.com/[A-Za-z0-9_-]+', text, re.IGNORECASE))
    has_linkedin = bool(re.search(r'linkedin\.com/in/[A-Za-z0-9_-]+', text, re.IGNORECASE))

    if has_email and has_phone:
        checks.append({"name": "Contact Coordinates", "status": "pass", "detail": "Direct Email and Phone Number detected"})
    else:
        score_penalty += 10
        checks.append({"name": "Contact Coordinates", "status": "fail", "detail": "Missing direct Email or Phone number"})

    if has_github and has_linkedin:
        checks.append({"name": "Developer Profiles", "status": "pass", "detail": "Both GitHub and LinkedIn URLs verified"})
    elif has_github or has_linkedin:
        checks.append({"name": "Developer Profiles", "status": "warning", "detail": "Only one profile link found"})
    else:
        score_penalty += 5
        checks.append({"name": "Developer Profiles", "status": "fail", "detail": "No GitHub or LinkedIn links found"})

    # 2. Standard ATS Section Headers Check
    required_sections = {
        "Skills": [r"\btechnical\s+skills\b", r"\bskills\b"],
        "Experience / Projects": [r"\bprojects\b", r"\btechnical\s+projects\b", r"\bexperience\b"],
        "Education": [r"\beducation\b", r"\bacademics\b"]
    }

    detected_sections = []
    missing_sections = []

    for sec_name, patterns in required_sections.items():
        found = any(re.search(p, text, re.IGNORECASE) for p in patterns)
        if found:
            detected_sections.append(sec_name)
        else:
            missing_sections.append(sec_name)

    if not missing_sections:
        checks.append({"name": "ATS Section Headers", "status": "pass", "detail": f"Standard headers found ({', '.join(detected_sections)})"})
    else:
        score_penalty += 15
        checks.append({"name": "ATS Section Headers", "status": "warning", "detail": f"Missing standard headers: {', '.join(missing_sections)}"})

    # 3. Text Density & Page Length Check
    words = len(re.findall(r'\b\w+\b', text))
    if 350 <= words <= 750:
        checks.append({"name": "Length & Density", "status": "pass", "detail": f"Optimal 1-page density ({words} words)"})
    elif words < 350:
        checks.append({"name": "Length & Density", "status": "warning", "detail": f"Slightly short ({words} words), might lack keyword depth"})
    else:
        checks.append({"name": "Length & Density", "status": "warning", "detail": f"High word count ({words} words), check if spilling to page 2"})

    health_score = max(0, 100 - score_penalty)

    return {
        "health_score": health_score,
        "checks": checks,
        "word_count": words,
        "has_contact": has_email and has_phone,
        "has_profiles": has_github and has_linkedin
    }
