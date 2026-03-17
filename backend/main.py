# backend/main.py

import os
import shutil
import threading
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

import sys
sys.path.append(os.path.dirname(__file__))
from rag_service import RAGService


# ── Load environment variables ──
load_dotenv()

# ── Initialize app ──
app = FastAPI(title="Luminara RAG API")

# ── CORS configuration ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins in production; restrict in dev if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Initialize RAG Service ──
rag_service = RAGService()
chat_history: list = []

# Track background embedding jobs: filename → "processing" | "ready" | "error"
processing_status: dict = {}
processing_lock = threading.Lock()

# ── Models ──
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []

# ── Background embedding ──
def _embed_in_background(file_path: str, filename: str):
    try:
        rag_service.embed_document(file_path)
        with processing_lock:
            processing_status[filename] = "ready"
        print(f"[background] Embedding complete: {filename}")
    except Exception as e:
        with processing_lock:
            processing_status[filename] = f"error: {e}"
        print(f"[background] Embedding failed for {filename}: {e}")

# ── API Endpoints ──
@app.post("/upload")
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.endswith((".pdf", ".txt", ".csv")):
        raise HTTPException(status_code=400, detail="Only PDF, TXT, and CSV files are supported.")
    try:
        os.makedirs(rag_service.data_path, exist_ok=True)
        file_path = os.path.join(rag_service.data_path, file.filename)

        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Mark as processing
        with processing_lock:
            processing_status[file.filename] = "processing"

        # Start background embedding
        background_tasks.add_task(_embed_in_background, file_path, file.filename)

        return {
            "filename": file.filename,
            "message": "File saved. Embedding in background — you can start asking questions in a moment.",
            "status": "processing",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

@app.get("/status/{filename}")
async def get_file_status(filename: str):
    with processing_lock:
        status = processing_status.get(filename, "unknown")
    return {"filename": filename, "status": status}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        answer, sources = rag_service.query(request.query)
        chat_history.append({
            "query": request.query,
            "answer": answer,
            "sources": sources,
        })
        return ChatResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@app.get("/history")
async def get_history():
    return {"history": chat_history}

@app.get("/health")
async def health():
    return {"status": "ok"}

# ── Serve React frontend ──
frontend_dist = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")

# ── Run app (for local dev only) ──
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)