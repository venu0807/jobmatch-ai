# Question bank mapped to core skills with verified 60-second answer blueprints
QUESTION_BANK = {
    "Python": {
        "question": "What is the difference between mutable and immutable types in Python, and how does Python manage memory?",
        "answer_hint": "Mutable objects (list, dict, set) can be modified in place with same id. Immutable objects (int, float, str, tuple) allocate new objects on modification. Python uses reference counting + cyclic garbage collection with generations (0, 1, 2)."
    },
    "Django": {
        "question": "Explain the difference between select_related and prefetch_related in Django ORM with an example.",
        "answer_hint": "select_related performs an SQL INNER/LEFT JOIN for Single-valued relationships (ForeignKey, OneToOne). prefetch_related executes a separate SQL query and joins in Python memory for Multi-valued relationships (ManyToMany). Used in my Movie project to eliminate N+1 queries."
    },
    "Django REST Framework": {
        "question": "How do you implement custom permissions and writable nested serializers in DRF?",
        "answer_hint": "Inherit from BasePermission and override has_permission or has_object_permission (e.g. IsOwnerOrReadOnly). For writable nested serializers, override create() and update() to pop nested child dictionaries and create related model instances."
    },
    "PostgreSQL": {
        "question": "How do B-tree indexes work in PostgreSQL, and when would an index scan NOT be used?",
        "answer_hint": "B-trees maintain a balanced search tree in O(log n) time. The query planner ignores indexes if: 1) table is too small (Seq Scan is faster), 2) low cardinality column (e.g. boolean), 3) functions applied on indexed columns (LOWER(title)), or 4) query matches >20% of the entire table."
    },
    "Redis": {
        "question": "Explain the Cache-Aside pattern and how you handle cache expiration and invalidation.",
        "answer_hint": "Application queries Redis first. On cache hit, return immediately. On cache miss, fetch from PostgreSQL, write to Redis with a TTL (e.g., 3600s), and return. On record update/delete, invalidate or delete the Redis key to avoid stale data."
    },
    "Docker": {
        "question": "What is a multi-stage Docker build, and why is it important for production Python deployments?",
        "answer_hint": "Separates the build environment (compilers, build-essential, header files) from the minimal runtime image (python:slim + runtime libraries). Shrinks image size by 60-80% and removes attack surface/security vulnerabilities."
    },
    "PyTest": {
        "question": "What is the purpose of PyTest fixtures and conftest.py?",
        "answer_hint": "Fixtures provide modular, reusable test dependencies with scopes (function, class, module, session). conftest.py allows sharing fixtures and hooks across the entire test suite without importing them explicitly."
    },
    "React.js": {
        "question": "Explain the difference between useCallback, useMemo, and React.memo.",
        "answer_hint": "React.memo is an HOC that prevents component re-render if props are shallowly equal. useMemo caches the computed result of an expensive calculation. useCallback caches the function instance itself so child components don't re-render on re-created callbacks."
    },
    "Scikit-learn": {
        "question": "How did you build the recommendation algorithm using TF-IDF and Cosine Similarity?",
        "answer_hint": "Combined movie features into a metadata soup string. Computed TF-IDF vectors (Term Frequency x Inverse Document Frequency). Calculated pairwise Cosine Similarity (dot product / magnitude product). Output top-10 highest similarity scores in O(1) from pre-calculated matrix."
    },
    "TensorFlow": {
        "question": "Why use a 2D CNN for audio classification instead of a 1D model or RNN?",
        "answer_hint": "Raw audio was transformed into 2D Mel Spectrograms (Frequency vs Time in decibels) using Librosa. Mel spectrograms display 2D spatial coherence for acoustic signatures (screams, gunshots). Convolutions slide across both axes and are highly parallelizable on mobile NPUs via TFLite (sub-100ms)."
    },
    "REST APIs": {
        "question": "What is idempotency in REST APIs? Which HTTP methods are idempotent and why?",
        "answer_hint": "An operation is idempotent if executing it multiple times produces the identical server state as executing it once. GET, PUT, and DELETE are idempotent. POST is NOT idempotent (creates duplicate resources). PATCH is generally non-idempotent."
    },
    "JWT": {
        "question": "Why is storing JWT tokens in localStorage risky, and what is the recommended industry pattern?",
        "answer_hint": "localStorage is vulnerable to XSS (malicious scripts can read window.localStorage). Best practice: Store short-lived Access Token in React memory, and Refresh Token in an HttpOnly, Secure, SameSite=Strict cookie inaccessible to JavaScript, using token rotation."
    },
    "FastAPI": {
        "question": "How does FastAPI achieve high performance, and how does dependency injection work in it?",
        "answer_hint": "Built on Starlette (asyncio) and Pydantic (data parsing/validation). Executes asynchronous I/O natively with async def. Dependency Injection (Depends) allows modular sharing of database sessions, auth checks, and configurations across endpoints."
    },
    "Playwright": {
        "question": "Why choose Playwright over Selenium for modern browser automation?",
        "answer_hint": "Playwright connects directly via Chrome DevTools Protocol (CDP) over a single WebSocket (3x faster than WebDriver HTTP calls). Includes automatic waiting on actionable elements (eliminating sleep hacks) and isolated browser contexts without cookie pollution."
    }
}

DEFAULT_QUESTIONS = [
    {
        "question": "Walk me through the architecture of your Movie Recommendation platform.",
        "answer_hint": "DRF backend + React.js frontend. Normalized PostgreSQL schema with composite B-tree index (genre, rating DESC) cutting query latency by 60%. Content-based TF-IDF and Cosine similarity recommendation engine, cached with Redis."
    },
    {
        "question": "Explain a difficult technical bug you solved in your projects.",
        "answer_hint": "In the Jarvis automation engine, job portals changed dynamic DOM elements and rate-limited calls. Solved by migrating to an event-driven decoupled architecture with exponential backoff retries, reaching 99% reliability across 200+ applications."
    }
]

def predict_interview_questions(matched_skills: list, missing_skills: list) -> list:
    """
    Picks top 5 most relevant interview questions tailored to the skills demanded by this specific job.
    """
    predicted = []
    selected_skills = set()

    # Prioritize matched skills first (interviewer will test what you know)
    for skill in matched_skills:
        if skill in QUESTION_BANK and skill not in selected_skills:
            predicted.append({
                "skill": skill,
                "category": "Core Requirement",
                "question": QUESTION_BANK[skill]["question"],
                "answer_hint": QUESTION_BANK[skill]["answer_hint"]
            })
            selected_skills.add(skill)
        if len(predicted) >= 3:
            break

    # Next, include questions on missing/demanded skills (interviewer will probe the gap)
    for skill in missing_skills:
        if skill in QUESTION_BANK and skill not in selected_skills:
            predicted.append({
                "skill": skill,
                "category": "Potential Skill Gap Test",
                "question": QUESTION_BANK[skill]["question"],
                "answer_hint": QUESTION_BANK[skill]["answer_hint"]
            })
            selected_skills.add(skill)
        if len(predicted) >= 5:
            break

    # Fallback to general high-frequency architectural questions if needed
    while len(predicted) < 5:
        idx = len(predicted) % len(DEFAULT_QUESTIONS)
        default_item = DEFAULT_QUESTIONS[idx]
        predicted.append({
            "skill": "Project Architecture",
            "category": "System Design & Experience",
            "question": default_item["question"],
            "answer_hint": default_item["answer_hint"]
        })

    return predicted[:5]
