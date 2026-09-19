import re

# Comprehensive Tech Skills Taxonomy with Aliases and Categories
TECH_TAXONOMY = {
    "Languages": {
        "Python": [r"\bpython\b", r"\bpython3\b"],
        "Java": [r"\bjava\b(?!\s*script)"],
        "JavaScript": [r"\bjavascript\b", r"\bjs\b", r"\bes6\b", r"\bes20\d{2}\b"],
        "TypeScript": [r"\btypescript\b", r"\bts\b"],
        "SQL": [r"\bsql\b", r"\bpl/sql\b"],
        "C++": [r"\bc\+\+\b", r"\bcpp\b"],
        "C#": [r"\bc#\b", r"\bcsharp\b"],
        "Go": [r"\bgolang\b", r"\bgo\s+language\b", r"\bgo\b(?=\s*(?:developer|backend|engineer))"],
        "Rust": [r"\brust\b(?=\s*(?:lang|developer|engineer))?"],
        "Bash/Shell": [r"\bbash\b", r"\bshell\s+script(?:ing)?\b", r"\bsh\b"]
    },
    "Backend & Frameworks": {
        "Django": [r"\bdjango\b"],
        "Django REST Framework": [r"\bdjango\s+rest\s+framework\b", r"\bdrf\b"],
        "FastAPI": [r"\bfastapi\b", r"\bfast\s+api\b"],
        "Flask": [r"\bflask\b"],
        "REST APIs": [r"\brest\s*api[s]?\b", r"\brestful\b", r"\brest\b(?=\s*(?:api|services|endpoints))"],
        "JWT": [r"\bjwt\b", r"\bjson\s*web\s*token[s]?\b"],
        "Node.js": [r"\bnode(?:\.js)?\b"],
        "Express.js": [r"\bexpress(?:\.js)?\b"],
        "Spring Boot": [r"\bspring\s*boot\b", r"\bspring\s*framework\b"],
        "GraphQL": [r"\bgraphql\b"],
        "Microservices": [r"\bmicroservices\b", r"\bmicroservice\s+architecture\b"],
        "WebSockets": [r"\bwebsocket[s]?\b"]
    },
    "Frontend": {
        "React.js": [r"\breact(?:\.js)?\b"],
        "HTML5": [r"\bhtml5?\b"],
        "CSS3": [r"\bcss3?\b"],
        "Bootstrap": [r"\bbootstrap(?:5)?\b"],
        "Tailwind CSS": [r"\btailwind(?:\s*css)?\b"],
        "Redux": [r"\bredux\b", r"\bredux\s+toolkit\b"],
        "Next.js": [r"\bnext(?:\.js)?\b"],
        "Vue.js": [r"\bvue(?:\.js)?\b"],
        "Responsive UI": [r"\bresponsive\s*(?:ui|design|web)\b"]
    },
    "Databases & Caching": {
        "PostgreSQL": [r"\bpostgres(?:ql)?\b"],
        "MySQL": [r"\bmysql\b"],
        "Redis": [r"\bredis\b"],
        "MongoDB": [r"\bmongodb\b", r"\bmongo\b"],
        "SQLite": [r"\bsqlite3?\b"],
        "Cassandra": [r"\bcassandra\b"],
        "DynamoDB": [r"\bdynamodb\b"],
        "Schema Design": [r"\bschema\s+design\b", r"\bdatabase\s+modeling\b"],
        "Query Optimization": [r"\bquery\s+optimization\b", r"\bquery\s+tuning\b", r"\bperformance\s+tuning\b"],
        "B-tree Indexing": [r"\bb-?tree\b", r"\bindexing\b", r"\bdatabase\s+index(?:es)?\b"],
        "Django ORM": [r"\bdjango\s+orm\b", r"\borm\b(?=\s*(?:queries|django|methods))"]
    },
    "Machine Learning & AI": {
        "Scikit-learn": [r"\bscikit-?learn\b", r"\bsklearn\b"],
        "TensorFlow": [r"\btensorflow\b", r"\btf\b(?=\s*(?:keras|lite|model))"],
        "TFLite": [r"\btflite\b", r"\btensorflow\s*lite\b"],
        "CNN": [r"\bcnn\b", r"\bconvolutional\s+neural\s+network[s]?\b"],
        "Deep Learning": [r"\bdeep\s+learning\b", r"\bdl\b(?=\s*(?:models|engineer))"],
        "NLP": [r"\bnlp\b", r"\bnatural\s+language\s+processing\b"],
        "Pandas": [r"\bpandas\b"],
        "NumPy": [r"\bnumpy\b"],
        "Feature Engineering": [r"\bfeature\s+engineering\b"],
        "Model Quantization": [r"\bmodel\s+quantization\b", r"\bint8\b", r"\bquantization\b"],
        "PyTorch": [r"\bpytorch\b"],
        "LangChain": [r"\blangchain\b"],
        "LlamaIndex": [r"\bllamaindex\b"],
        "RAG": [r"\brag\b", r"\bretrieval\s+augmented\s+generation\b"],
        "ChromaDB": [r"\bchromadb\b", r"\bchroma\b(?=\s*(?:db|vector))"],
        "Vector Databases": [r"\bvector\s+(?:db|database[s]?|store[s]?)\b"]
    },
    "DevOps, Cloud & Automation": {
        "Docker": [r"\bdocker\b"],
        "Docker Compose": [r"\bdocker-?compose\b"],
        "Git": [r"\bgit\b(?!\s*hub|\s*lab)"],
        "GitHub": [r"\bgithub\b"],
        "GitHub Actions": [r"\bgithub\s*actions\b"],
        "CI/CD": [r"\bci/cd\b", r"\bcontinuous\s+integration\b"],
        "AWS": [r"\baws\b", r"\bamazon\s+web\s+services\b", r"\bec2\b", r"\bs3\b"],
        "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
        "Celery": [r"\bcelery\b"],
        "Linux": [r"\blinux\b", r"\bubuntu\b"],
        "Nginx": [r"\bnginx\b"]
    },
    "Testing & Quality": {
        "PyTest": [r"\bpytest\b", r"\bpy\.test\b"],
        "Playwright": [r"\bplaywright\b"],
        "BeautifulSoup": [r"\bbeautifulsoup4?\b", r"\bbs4\b"],
        "Unit Testing": [r"\bunit\s*test(?:ing)?\b", r"\bunittest\b"],
        "TDD": [r"\btdd\b", r"\btest\s*driven\s*development\b"]
    },
    "Core CS & Architecture": {
        "OOP": [r"\boop\b", r"\bobject\s*oriented\s*programming\b"],
        "DSA": [r"\bdsa\b", r"\bdata\s*structures\b", r"\balgorithms\b"],
        "System Design": [r"\bsystem\s*design\b", r"\bhigh\s*level\s*design\b", r"\bhld\b"],
        "SOLID Principles": [r"\bsolid\b(?=\s*(?:principles|design|patterns))"],
        "Design Patterns": [r"\bdesign\s*patterns?\b"]
    }
}

def extract_skills_from_text(text: str) -> dict:
    """
    Scans text against the tech taxonomy and returns:
    - 'found_skills': list of normalized skill names
    - 'by_category': dict of skills grouped by category
    """
    found_skills = set()
    by_category = {}
    normalized_text = text.lower()

    for category, skills_dict in TECH_TAXONOMY.items():
        by_category[category] = []
        for skill_name, patterns in skills_dict.items():
            for pattern in patterns:
                if re.search(pattern, normalized_text, re.IGNORECASE):
                    found_skills.add(skill_name)
                    by_category[category].append(skill_name)
                    break  # Found this skill, move to next
        if not by_category[category]:
            del by_category[category]

    return {
        "found_skills": sorted(list(found_skills)),
        "by_category": by_category
    }
