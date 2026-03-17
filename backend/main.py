import os
import shutil
import threading
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from rag_service import RAGService

load_dotenv()

app = FastAPI(title="Luminara RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = RAGService()
chat_history: list = []

# Track background embedding jobs: filename → "processing" | "ready" | "error"
processing_status: dict = {}
processing_lock = threading.Lock()


# Models for request/response validation

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str] = []


# Background embedding function — runs in a thread pool to avoid blocking the main event loop

def _embed_in_background(file_path: str, filename: str):
    """Runs in a thread pool; updates processing_status when done."""
    try:
        rag_service.embed_document(file_path)
        with processing_lock:
            processing_status[filename] = "ready"
        print(f"[background] Embedding complete: {filename}")
    except Exception as e:
        with processing_lock:
            processing_status[filename] = f"error: {e}"
        print(f"[background] Embedding failed for {filename}: {e}")


# API Endpoints

@app.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Save the file to disk immediately and return a 200 response.
    Embedding happens in the background so the frontend is not blocked.
    """
    if not file.filename.endswith((".pdf", ".txt", ".csv")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT, and CSV files are supported.",
        )

    try:
        os.makedirs(rag_service.data_path, exist_ok=True)
        file_path = os.path.join(rag_service.data_path, file.filename)

        # Save file to disk — fast
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Mark as processing
        with processing_lock:
            processing_status[file.filename] = "processing"

        # Schedule embedding in a background thread — does NOT block the response
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
    """Poll this to check if a file has finished embedding."""
    with processing_lock:
        status = processing_status.get(filename, "unknown")
    return {"filename": filename, "status": status}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Answer a question using RAG with MMR retrieval and detailed prompting."""
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
