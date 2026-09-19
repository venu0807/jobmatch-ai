def generate_tailoring_recommendations(missing_skills: list, matched_skills: list, jd_text: str) -> list:
    """
    Generates actionable, honest resume tailoring tips based on missing skills.
    """
    recommendations = []

    # Check for common missing tech and provide honest project-proven framings
    skill_advice_map = {
        "FastAPI": "JD mentions FastAPI. Add 'FastAPI' under Backend Skills or mention: 'Familiar with async API development via FastAPI & Pydantic'.",
        "AWS": "JD mentions AWS. Frame honestly: 'Studied cloud deployment concepts (EC2, S3); deployed containerized Django/PostgreSQL services via Docker'.",
        "Celery": "JD mentions Celery. Mention: 'Built event-driven worker daemons and background tasks in Python; understand task queues and broker architecture'.",
        "Kubernetes": "JD mentions Kubernetes/K8s. Frame as: 'Familiar with container orchestration concepts and microservice scaling; experienced with Docker & Compose'.",
        "Redis": "Ensure Redis caching is explicitly highlighted in your Movie Recommendation bullet (e.g. 'applied Redis caching with B-tree indexing').",
        "Docker": "Highlight Docker containerization in your Movie Recommender or personal setup.",
        "PyTest": "Make sure PyTest is clearly visible under DevOps & Tools (critical quality keyword).",
        "GraphQL": "If asked, frame as: 'Deep REST API & JSON architecture background; familiar with GraphQL schema and query resolver concepts'.",
        "Linux": "Mention your command-line environment and Git terminal proficiency."
    }

    for skill in missing_skills:
        if skill in skill_advice_map:
            recommendations.append({
                "type": "missing_keyword",
                "skill": skill,
                "tip": skill_advice_map[skill]
            })

    # If general missing skills exist
    other_missing = [s for s in missing_skills if s not in skill_advice_map]
    if other_missing:
        recommendations.append({
            "type": "general_keywords",
            "skill": ", ".join(other_missing[:4]),
            "tip": f"Consider adding familiar concepts or coursework for {', '.join(other_missing[:4])} if relevant."
        })

    # Strengths to emphasize
    if "Django" in matched_skills and "PostgreSQL" in matched_skills:
        recommendations.append({
            "type": "strength_highlight",
            "skill": "Django & PostgreSQL",
            "tip": "Strong Match: Emphasize your 60% query latency cut and B-tree indexing in the interview!"
        })

    if "Playwright" in matched_skills or "Python" in matched_skills:
        recommendations.append({
            "type": "strength_highlight",
            "skill": "Python Automation",
            "tip": "Highlight your Jarvis automation engine (200+ applications processed with 99% reliability)."
        })

    return recommendations

def generate_recruiter_outreach_dm(matched_skills: list, missing_skills: list) -> str:
    """
    Drafts a personalized, high-converting LinkedIn DM to HR/Tech Leads for this job.
    """
    top_matches = ", ".join(matched_skills[:4]) if matched_skills else "Python, Django, React, PostgreSQL"
    
    dm = (
        f"Hi [Hiring Manager / Recruiter Name],\n\n"
        f"I came across the Python Developer role at your team and was excited to see the focus on {top_matches}.\n\n"
        f"I am a Python Full Stack Developer with hands-on experience building production systems:\n"
        f"• Built an ML-integrated movie recommendation platform (Django, React, PostgreSQL) cutting query latency by 60% via B-tree indexing.\n"
        f"• Deployed real-time CNN threat detection models with sub-100ms TFLite inference.\n"
        f"• Solved 500+ LeetCode problems (Top 8% nationally in AlgoUniversity).\n\n"
        f"I am relocating to Hyderabad and available for immediate joining. I'd love to share my resume if you're open to a quick chat.\n\n"
        f"Best regards,\nVenu Gopal Reddy Palugulla\n+91 6309343563 | linkedin.com/in/venu0807/"
    )
    return dm
