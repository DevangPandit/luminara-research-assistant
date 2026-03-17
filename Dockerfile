# Stage 1 - Build frontend
FROM node:20-slim AS frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2 - Python backend
FROM python:3.11-slim

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy built frontend from stage 1
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Install CPU-only PyTorch first (much smaller than default)
RUN pip install --no-cache-dir \
    torch==2.2.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    langchain \
    langchain-groq \
    langchain-huggingface \
    langchain-chroma \
    langchain-community \
    chromadb \
    sentence-transformers \
    pypdf \
    python-dotenv \
    python-multipart \
    aiofiles

# Copy backend code
COPY backend/ ./backend/
COPY data/ ./data/

EXPOSE 8080

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]