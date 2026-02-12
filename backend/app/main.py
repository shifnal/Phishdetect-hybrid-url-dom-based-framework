"""
PhishDetect Backend - Main Application Entry Point
"""

# ---------------------------
# CRITICAL: Fix Python path FIRST
# ---------------------------
import sys
import os
from pathlib import Path

# Resolve project root: main-project/
ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# ---------------------------
# Now safe to import everything
# ---------------------------
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from app.api.routes import router, set_paths
from app.ml.url_predictor import initialize_model

# ---------------------------
# Directories
# ---------------------------
BASE_DIR = Path(__file__).resolve().parent          # backend/app/
BACKEND_DIR = BASE_DIR.parent                      # backend/
MODELS_DIR = ROOT_DIR / "models"                   # main-project/models
FRONTEND_DIR = ROOT_DIR / "frontend" / "src"       # main-project/frontend/src
SCRIPTS_DIR = BACKEND_DIR / "scripts"              # backend/scripts

print(f"Root Dir      : {ROOT_DIR}")
print(f"Models Dir   : {MODELS_DIR}")
print(f"Frontend Dir : {FRONTEND_DIR}")
print(f"Scripts Dir  : {SCRIPTS_DIR}")

# ---------------------------
# Initialize ML Model
# ---------------------------
try:
    initialize_model(str(MODELS_DIR))
except Exception as e:
    print(f"❌ Error loading model: {e}")
    raise

# ---------------------------
# Set paths for API routes
# ---------------------------
set_paths(str(FRONTEND_DIR), str(SCRIPTS_DIR))

# ---------------------------
# FastAPI app
# ---------------------------
app = FastAPI(
    title="PhishDetect API",
    description="Hybrid URL-DOM-Visual Phishing Detection Framework",
    version="2.0.0"
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["phishdetect-url-dom-hybrid-framework.netlify.app"],  # Replace with your Netlify URL
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Static Frontend
# ---------------------------
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
    print(f"✓ Static files mounted from: {FRONTEND_DIR}")
else:
    print(f"⚠ Frontend directory not found: {FRONTEND_DIR}")

# ---------------------------
# Routes
# ---------------------------
app.include_router(router)

@app.get("/", response_class=HTMLResponse)
async def home():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return index_path.read_text()
    return "<h1>PhishDetect API</h1><p>Frontend not found. API is running.</p>"

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "phishdetect"}

# ---------------------------
# Local run
# ---------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
