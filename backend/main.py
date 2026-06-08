import os
import hashlib
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import threading
from parser.analyzer import analyze_code

app = FastAPI(title="AI-Assisted Code Intent & Risk Analyzer API")

# Enable CORS for integration with VS Code extensions or external frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    code: str

# Simple in-memory cache to prevent overheating/unnecessary CPU usage
ANALYSIS_CACHE = {}
MAX_CACHE_SIZE = 100
cache_lock = threading.Lock()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(CURRENT_DIR, "index.html")

@app.get("/", response_class=HTMLResponse)
def home():
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CodeSense AI Backend</title>
        </head>
        <body style="background:#080c14; color:#fff; font-family:sans-serif; text-align:center; padding-top:100px;">
            <h1>CodeSense AI Backend</h1>
            <p style="color:#9ca3af;">index.html not found. Place it in the backend folder.</p>
        </body>
        </html>
        """

@app.post("/analyze")
def analyze(payload: AnalyzeRequest):
    try:
        # Generate SHA-256 hash of the code to use as the cache key
        code_hash = hashlib.sha256(payload.code.encode("utf-8")).hexdigest()
        
        # Check cache under lock
        with cache_lock:
            if code_hash in ANALYSIS_CACHE:
                return ANALYSIS_CACHE[code_hash]
            
        # Run analysis (outside lock to avoid blocking other threads)
        result = analyze_code(payload.code)
        
        # Cache results under lock with eviction if size exceeds threshold
        with cache_lock:
            if code_hash not in ANALYSIS_CACHE:
                if len(ANALYSIS_CACHE) >= MAX_CACHE_SIZE:
                    oldest_key = next(iter(ANALYSIS_CACHE))
                    ANALYSIS_CACHE.pop(oldest_key, None)
                ANALYSIS_CACHE[code_hash] = result
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "2.0.0",
        "engine": "CodeSense AI",
        "rules_count": 5,
        "features": [
            "ast_parsing", "risk_detection", "intent_prediction",
            "complexity_analysis", "architecture_smells",
            "call_graph", "dependency_graph"
        ]
    }