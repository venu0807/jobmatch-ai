import math
import re
from collections import Counter
from .taxonomy import TECH_TAXONOMY, extract_skills_from_text
from .evidence import find_evidence_snippet

def compute_pure_python_tfidf_similarity(text1: str, text2: str) -> float:
    """
    Lightweight fallback TF-IDF Cosine Similarity implementation in pure Python.
    Guarantees 100% execution even if scikit-learn is not installed.
    """
    def tokenize(text):
        return re.findall(r'\b[a-zA-Z0-9+#.-]{2,}\b', text.lower())

    tokens1 = tokenize(text1)
    tokens2 = tokenize(text2)

    if not tokens1 or not tokens2:
        return 0.0

    tf1 = Counter(tokens1)
    tf2 = Counter(tokens2)

    vocab = set(tf1.keys()).union(set(tf2.keys()))
    num_docs = 2

    vec1 = []
    vec2 = []

    for word in vocab:
        df = (1 if word in tf1 else 0) + (1 if word in tf2 else 0)
        idf = math.log((num_docs + 1) / (df + 1)) + 1.0

        w1 = (1 + math.log(tf1[word])) * idf if tf1[word] > 0 else 0.0
        w2 = (1 + math.log(tf2[word])) * idf if tf2[word] > 0 else 0.0

        vec1.append(w1)
        vec2.append(w2)

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a * a for a in vec1))
    mag2 = math.sqrt(sum(b * b for b in vec2))

    if mag1 == 0 or mag2 == 0:
        return 0.0

    return dot_product / (mag1 * mag2)

def compute_semantic_similarity(resume_text: str, jd_text: str) -> float:
    """
    Computes semantic similarity using Scikit-learn if available, otherwise pure Python.
    """
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        vectorizer = TfidfVectorizer(stop_words='english', token_pattern=r'(?u)\b[a-zA-Z0-9+#.-]{2,}\b')
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(sim)
    except Exception:
        return compute_pure_python_tfidf_similarity(resume_text, jd_text)

def match_resume_to_jd(resume_text: str, jd_text: str) -> dict:
    """
    Performs transparent, evidence-grounded ATS matching with zero hallucinations.
    """
    resume_skills_info = extract_skills_from_text(resume_text)
    jd_skills_info = extract_skills_from_text(jd_text)

    resume_skills = set(resume_skills_info["found_skills"])
    jd_skills = set(jd_skills_info["found_skills"])

    matched_skill_names = sorted(list(resume_skills.intersection(jd_skills)))
    missing_skill_names = sorted(list(jd_skills.difference(resume_skills)))
    bonus_skill_names = sorted(list(resume_skills.difference(jd_skills)))

    # Generate grounded evidence quotes for every skill from the real text
    matched_skills_with_evidence = []
    for s in matched_skill_names:
        patterns = []
        for cat in TECH_TAXONOMY.values():
            if s in cat:
                patterns = cat[s]
                break
        jd_evidence = find_evidence_snippet(jd_text, patterns)
        resume_evidence = find_evidence_snippet(resume_text, patterns)
        matched_skills_with_evidence.append({
            "name": s,
            "jd_quote": jd_evidence,
            "resume_quote": resume_evidence
        })

    missing_skills_with_evidence = []
    for s in missing_skill_names:
        patterns = []
        for cat in TECH_TAXONOMY.values():
            if s in cat:
                patterns = cat[s]
                break
        jd_evidence = find_evidence_snippet(jd_text, patterns)
        missing_skills_with_evidence.append({
            "name": s,
            "jd_quote": jd_evidence
        })

    # 1. Skill Coverage Score (0 - 100)
    if jd_skills:
        skill_coverage_score = (len(matched_skill_names) / len(jd_skills)) * 100.0
    else:
        skill_coverage_score = 80.0

    # 2. Semantic Similarity Score (0 - 100)
    # In cross-corpus comparison between a full resume (500+ words) and a typical JD (70-300 words),
    # TF-IDF cosine naturally centers around 0.15-0.35.
    # Normalizing against realistic ATS thresholds maps strong contextual alignment (0.28+) to 80-95%.
    raw_sim = compute_semantic_similarity(resume_text, jd_text)
    semantic_score = min(100.0, max(0.0, round((raw_sim / 0.30) * 85.0, 1)))

    # 3. Composite ATS Score (Weighted: 70% Hard Skills + 30% Semantic Fit)
    composite_ats_score = round((0.70 * skill_coverage_score) + (0.30 * semantic_score), 1)
    composite_ats_score = min(99.0, max(15.0, composite_ats_score))

    # Grade Rating
    if composite_ats_score >= 85:
        rating = "Excellent Match"
        rating_color = "emerald"
        action_advice = "Your verified skills strongly match the job requirements. High likelihood of passing ATS filter."
    elif composite_ats_score >= 70:
        rating = "Good Match"
        rating_color = "blue"
        action_advice = "Strong foundation. Review the missing skill evidence below and adjust 1-2 bullet points before applying."
    elif composite_ats_score >= 50:
        rating = "Moderate Match"
        rating_color = "amber"
        action_advice = "Noticeable gaps in requested stack. Check the missing requirements below to decide if you want to frame them."
    else:
        rating = "Low Match"
        rating_color = "rose"
        action_advice = "Significant stack divergence. High probability of automatic screening rejection."

    return {
        "ats_score": composite_ats_score,
        "skill_coverage_score": round(skill_coverage_score, 1),
        "semantic_score": round(semantic_score, 1),
        "raw_cosine_similarity": round(raw_sim, 3),
        "rating": rating,
        "rating_color": rating_color,
        "action_advice": action_advice,
        "matched_skills": matched_skill_names,
        "matched_skills_with_evidence": matched_skills_with_evidence,
        "missing_skills": missing_skill_names,
        "missing_skills_with_evidence": missing_skills_with_evidence,
        "bonus_skills": bonus_skill_names[:8],
        "jd_skills_count": len(jd_skills),
        "matched_skills_count": len(matched_skill_names),
        "scoring_formula": {
            "weight_skills": "70%",
            "weight_semantic": "30%",
            "formula_text": f"ATS Score = (0.70 × {round(skill_coverage_score, 1)}%) + (0.30 × {round(semantic_score, 1)}%) = {composite_ats_score}%"
        }
    }
