import sys
import os
import json
from pathlib import Path

# Add current directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from core.extractor import get_default_resume_text, extract_text_from_pdf_bytes
from core.matcher import match_resume_to_jd
from core.analyzer import generate_tailoring_recommendations, generate_recruiter_outreach_dm
from core.predictor import predict_interview_questions
from core.evidence import audit_resume_structure
from core.tailor import tailor_resume
from core.pdf_compiler import generate_tailored_pdf

import shutil

EXPORTS_DIR = BASE_DIR / "exports"
EXPORTS_DIR.mkdir(exist_ok=True)
LATEST_PDF_PATH = EXPORTS_DIR / "VenuGopalReddy_Tailored_Resume.pdf"
DEFAULT_PDF_SRC = BASE_DIR / "data" / "default_resume.pdf"

if DEFAULT_PDF_SRC.exists() and not LATEST_PDF_PATH.exists():
    try:
        shutil.copyfile(str(DEFAULT_PDF_SRC), str(LATEST_PDF_PATH))
    except Exception:
        pass

# Check if FastAPI is available
try:
    from fastapi import FastAPI, File, UploadFile, Request
    from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
    from pydantic import BaseModel
    import uvicorn

    app = FastAPI(title="JobMatch AI", description="Smart ATS Matcher, Skill-Gap Analyzer & Resume Tailor")

    class AnalyzeRequest(BaseModel):
        resume_text: str
        jd_text: str

    class TailorRequest(BaseModel):
        jd_text: str
        resume_text: str = ""

    @app.get("/", response_class=HTMLResponse)
    async def serve_index():
        template_path = BASE_DIR / "templates" / "index.html"
        with open(template_path, "r", encoding="utf-8") as f:
            return f.read()

    @app.get("/api/default-resume")
    async def api_default_resume():
        return get_default_resume_text()

    @app.post("/api/upload-resume")
    async def api_upload_resume(file: UploadFile = File(...)):
        try:
            content = await file.read()
            text = extract_text_from_pdf_bytes(content)
            return {"success": True, "text": text, "filename": file.filename}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.post("/api/analyze")
    async def api_analyze(req: AnalyzeRequest):
        match_data = match_resume_to_jd(req.resume_text, req.jd_text)
        tailoring = generate_tailoring_recommendations(match_data["missing_skills"], match_data["matched_skills"], req.jd_text)
        predicted_q = predict_interview_questions(match_data["matched_skills"], match_data["missing_skills"])
        dm = generate_recruiter_outreach_dm(match_data["matched_skills"], match_data["missing_skills"])
        health = audit_resume_structure(req.resume_text)

        response = {
            **match_data,
            "tailoring_tips": tailoring,
            "predicted_questions": predicted_q,
            "recruiter_dm": dm,
            "health_audit": health
        }
        return response

    @app.post("/api/tailor")
    async def api_tailor(req: TailorRequest):
        try:
            result = tailor_resume(req.jd_text, req.resume_text)
            
            # Automatically generate the tailored single-page PDF
            pdf_ok = generate_tailored_pdf(result["injected_skills"], req.jd_text, str(LATEST_PDF_PATH))
            if not pdf_ok and DEFAULT_PDF_SRC.exists() and not LATEST_PDF_PATH.exists():
                try:
                    shutil.copyfile(str(DEFAULT_PDF_SRC), str(LATEST_PDF_PATH))
                    pdf_ok = True
                except Exception:
                    pass
            result["pdf_ready"] = True
            result["pdf_url"] = "/api/download-tailored-pdf"
            
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    @app.get("/api/download-tailored-pdf")
    async def api_download_tailored_pdf():
        target_pdf = LATEST_PDF_PATH if LATEST_PDF_PATH.exists() else DEFAULT_PDF_SRC
        if target_pdf.exists():
            return FileResponse(
                path=str(target_pdf),
                media_type="application/pdf",
                filename="VenuGopalReddy_Tailored_Resume.pdf"
            )
        return JSONResponse({"error": "PDF not yet generated. Please click Auto-Tailor first."}, status_code=404)

    def run_server():
        port = int(os.environ.get("PORT", 7860 if os.environ.get("SPACE_ID") else 8000))
        host = os.environ.get("HOST", "0.0.0.0" if (os.environ.get("PORT") or os.environ.get("SPACE_ID")) else "127.0.0.1")
        print("=" * 60)
        print(f"🚀 JobMatch AI Server starting on http://{host}:{port}")
        print("=" * 60)
        if not os.environ.get("PORT") and not os.environ.get("SPACE_ID"):
            import webbrowser
            import threading
            threading.Timer(1.2, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
        uvicorn.run(app, host=host, port=port, log_level="info")

except ImportError:
    # Standalone fallback using Python's built-in http.server if FastAPI is not installed
    from http.server import HTTPServer, BaseHTTPRequestHandler

    class StandaloneHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/" or self.path == "/index.html":
                template_path = BASE_DIR / "templates" / "index.html"
                with open(template_path, "r", encoding="utf-8") as f:
                    content = f.read().encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            elif self.path == "/api/default-resume":
                data = get_default_resume_text()
                body = json.dumps(data).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif self.path == "/api/download-tailored-pdf":
                if LATEST_PDF_PATH.exists():
                    with open(LATEST_PDF_PATH, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/pdf")
                    self.send_header("Content-Disposition", 'attachment; filename="VenuGopalReddy_Tailored_Resume.pdf"')
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                else:
                    self.send_response(404)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

        def do_POST(self):
            if self.path == "/api/analyze":
                length = int(self.headers.get("Content-Length", 0))
                raw_data = self.rfile.read(length).decode("utf-8")
                req_json = json.loads(raw_data)
                
                resume_text = req_json.get("resume_text", "")
                jd_text = req_json.get("jd_text", "")

                match_data = match_resume_to_jd(resume_text, jd_text)
                tailoring = generate_tailoring_recommendations(match_data["missing_skills"], match_data["matched_skills"], jd_text)
                predicted_q = predict_interview_questions(match_data["matched_skills"], match_data["missing_skills"])
                dm = generate_recruiter_outreach_dm(match_data["matched_skills"], match_data["missing_skills"])
                health = audit_resume_structure(resume_text)

                response = {
                    **match_data,
                    "tailoring_tips": tailoring,
                    "predicted_questions": predicted_q,
                    "recruiter_dm": dm,
                    "health_audit": health
                }
                body = json.dumps(response).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            elif self.path == "/api/tailor":
                length = int(self.headers.get("Content-Length", 0))
                raw_data = self.rfile.read(length).decode("utf-8")
                req_json = json.loads(raw_data)
                
                jd_text = req_json.get("jd_text", "")
                resume_text = req_json.get("resume_text", "")

                try:
                    result = tailor_resume(jd_text, resume_text)
                    pdf_ok = generate_tailored_pdf(result["injected_skills"], jd_text, str(LATEST_PDF_PATH))
                    result["pdf_ready"] = pdf_ok
                    result["pdf_url"] = "/api/download-tailored-pdf" if pdf_ok else None
                except Exception as e:
                    result = {"success": False, "error": str(e)}

                body = json.dumps(result).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            else:
                self.send_response(404)
                self.end_headers()

    def run_server():
        print("=" * 60)
        print("🚀 JobMatch AI Server starting on http://127.0.0.1:8000 (Native HTTP)")
        print("Tip: Install fastapi & uvicorn for asynchronous mode: pip install fastapi uvicorn")
        print("=" * 60)
        server = HTTPServer(("127.0.0.1", 8000), StandaloneHandler)
        server.serve_forever()

if __name__ == "__main__":
    run_server()
