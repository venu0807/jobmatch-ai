---
title: JobMatch AI
emoji: 🎯
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# ⚡ JobMatch AI — Evidence-Based ATS Matcher, Resume Tailor & 1-Page Vector PDF Compiler

**JobMatch AI** is a production-grade NLP application that bridges the gap between candidate resumes and job descriptions. It calculates transparent, mathematically verified ATS match scores, highlights missing technical keywords, provides click-to-verify text evidence, automatically customizes your master resume without hallucinations, and compiles single-page vector PDFs ready to submit to recruiters.

---

## 🌟 Key Features

- **⚡ 1-Click Resume Auto-Load:** Automatically extracts text from PDF resumes using `pypdf`.
- **📐 100% Transparent ATS Scoring:** Weighted formula: $70\%$ Hard Skill Overlap + $30\%$ Scikit-Learn TF-IDF Cosine Similarity. Zero black-box hallucinations.
- **🔍 Click-to-Verify Grounded Evidence:** Every matched and missing skill displays literal sentence quotes from your resume and the job description side-by-side.
- **🛡️ Anti-Hallucination Honesty Safeguard:** Strictly excludes unlearned skills (`AWS`, `Celery`, `Nginx`, `Linux`, `Swagger`) from being falsely injected into your resume, providing verbal interview defense strategies instead.
- **✨ Surgical Master Resume Tailoring:** Injects verified matching skills into exact category lines while maintaining a strict 1-page layout.
- **📥 1-Click Vector PDF Compiler:** Headless Chromium/Edge native rendering compiles crisp, single-page vector PDFs (`VenuGopalReddy_Tailored_Resume.pdf`).
- **🎯 Recruiter Outreach DM Generator:** Instantly crafts personalized LinkedIn connection notes tailored to each job description.

---

## 🛠️ Architecture & Tech Stack

- **Backend:** Python 3.11, FastAPI, Uvicorn
- **NLP & Linear Algebra:** Scikit-Learn (TF-IDF Vectorizer & Cosine Distance), RegEx boundary taxonomy
- **Document Processing:** PyPDF, Headless Chromium Vector PDF Compiler
- **Frontend UI:** Responsive Tailwind CSS, Glassmorphism, Vanilla JS (zero external runtime dependencies)
- **Quality & Testing:** PyTest (10/10 automated tests passing)

---

## 🚀 Quick Start (Local)

### Windows
Double-click `run.bat` or run:
```powershell
pip install -r requirements.txt
python app.py
```
Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser.

### Docker
```bash
docker build -t jobmatch-ai .
docker run -p 7860:7860 jobmatch-ai
```
Open **[http://localhost:7860](http://localhost:7860)**.

---

## 🧪 Automated Testing

```powershell
pytest -v
```

---

## 👤 Author & Verified Profile

**Venu Gopal Reddy Palugulla**  
Python Full Stack Developer & MCA (AI & ML)  
- **LinkedIn:** [linkedin.com/in/venugopalreddy0807](https://www.linkedin.com/in/venugopalreddy0807/)  
- **GitHub:** [github.com/venu0807](https://github.com/venu0807)  
- **Portfolio:** [venureddy.vercel.app](https://venureddy.vercel.app/)
