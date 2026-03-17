# ✨ Luminara — AI Document Research Analyst
 
<div align="center">
 
![Luminara Banner](https://img.shields.io/badge/Luminara-AI%20Research%20Analyst-6366f1?style=for-the-badge&logo=sparkles&logoColor=white)
 
**Upload any document. Ask anything. Get precise answers instantly.**
 
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev)
[![Groq](https://img.shields.io/badge/Groq-LLaMA%203.3%2070B-f97316?style=flat-square)](https://groq.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-8b5cf6?style=flat-square)](https://www.trychroma.com)
[![Railway](https://img.shields.io/badge/Deploy-Railway-0f172a?style=flat-square&logo=railway&logoColor=white)](https://railway.app)
 
</div>
 
---
 
## 🧠 What is Luminara?
 
Luminara is a full-stack **RAG (Retrieval Augmented Generation)** application. Upload your PDFs, TXT, or CSV files and ask natural language questions — Luminara retrieves the most relevant context from your documents and generates precise, structured answers using **LLaMA 3.3 70B**.
 
```
User     →  "What are the key findings in this report?"
Luminara →  "Based on your document, the key findings are..."
```
 
---
 
## 🛠️ Tech Stack
 
| Layer | Technology |
|---|---|
| 🎨 Frontend | React + Vite + Tailwind CSS |
| ⚙️ Backend | FastAPI + Python |
| 🤖 LLM | LLaMA 3.3 70B via Groq API |
| 🔢 Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| 🗄️ Vector DB | ChromaDB |
| 📄 Doc Parsing | LangChain (PyPDFLoader, TextLoader, CSVLoader) |
 
---
 
## 📁 Project Structure
 
```
luminara/
├── backend/
│   ├── main.py              # FastAPI app + all endpoints
│   ├── rag_service.py       # Core RAG pipeline logic
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # For Railway deployment
│   ├── railway.json         # Railway config
│   └── .env                 # API keys (never commit this!)
│
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── data/                    # Uploaded documents (auto-created)
├── chroma_db/               # Vector store (auto-created)
├── .gitignore
└── README.md
```
 
---
 
## 🚀 Getting Started
 
### Prerequisites
 
- Python 3.10+
- Node.js 18+
- Groq API key — free at [console.groq.com](https://console.groq.com)
 
---
 
### 1️⃣ Clone the Repository
 
```bash
git clone https://github.com/DevangPandit/luminara-research-assistant.git
cd luminara-research-assistant
```
 
---
 
### 2️⃣ Backend Setup
 
```bash
cd backend
 
# Create virtual environment
python -m venv venv
 
# Activate — Windows
venv\Scripts\activate.bat
 
# Activate — Mac/Linux
source venv/bin/activate
 
# Install dependencies
pip install -r requirements.txt
```
 
Create a `.env` file inside `backend/`:
 
```env
GROQ_API_KEY=your_groq_api_key_here
```
 
Start the backend server:
 
```bash
uvicorn main:app --reload
```
 
> Backend runs at `http://localhost:8000`
> Auto API docs at `http://localhost:8000/docs`
 
---
 
### 3️⃣ Frontend Setup
 
```bash
cd frontend
npm install
npm run dev
```
 
> Frontend runs at `http://localhost:5173`
 
---
 
### 4️⃣ Using the App
 
1. Open `http://localhost:5173` in your browser
2. Upload a **PDF**, **TXT**, or **CSV** file
3. Wait a few seconds for embedding to complete
4. Ask any question about your document
5. Get a detailed answer powered by LLaMA 3.3 ✨
 
---
 
## 📡 API Endpoints
 
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/upload` | Upload a document for embedding |
| `GET` | `/status/{filename}` | Check embedding status |
| `POST` | `/chat` | Ask a question about uploaded docs |
| `GET` | `/history` | Retrieve chat history |
| `GET` | `/health` | Health check |
 
### Example Usage
 
```bash
# Upload a document
curl -X POST http://localhost:8000/upload \
  -F "file=@your_document.pdf"
 
# Ask a question
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic of this document?"}'
```
 
---
 
## 📦 Requirements
 
`backend/requirements.txt`
 
```
fastapi
uvicorn
python-dotenv
langchain
langchain-community
langchain-huggingface
langchain-chroma
langchain-groq
chromadb
pypdf
sentence-transformers
aiofiles
```
 
---
 
## 🔐 Environment Variables
 
| Variable | Description | Required |
|---|---|---|
| `GROQ_API_KEY` | Your Groq API key from console.groq.com | ✅ Yes |
 
---
 
## ☁️ Deployment
 
### Backend → Railway
 
#### Step 1: Create `Dockerfile` in `backend/`
 
```dockerfile
FROM python:3.11-slim
 
WORKDIR /app
 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
COPY . .
 
EXPOSE 8000
 
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```
 
#### Step 2: Create `railway.json` in `backend/`
 
```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "./Dockerfile"
  },
  "deploy": {
    "healthcheckPath": "/health",
    "restartPolicyType": "always"
  }
}
```
 
#### Step 3: Add `.gitignore` to project root
 
```gitignore
.env
venv/
__pycache__/
chroma_db/
data/
*.pyc
node_modules/
dist/
```
 
#### Step 4: Push to GitHub
 
```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/luminara.git
git push -u origin main
```
 
#### Step 5: Deploy on Railway
 
1. Go to [railway.com](https://railway.com) and sign in with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select your `luminara` repository
4. Railway auto-detects the Dockerfile and starts building ✅
 
#### Step 6: Add Environment Variable
 
1. Click your deployed service → **"Variables"** tab
2. Add `GROQ_API_KEY` = your Groq API key
3. Railway auto-redeploys ✅
 
#### Step 7: Generate Public URL
 
1. Go to **"Settings"** → **"Networking"**
2. Click **"Generate Domain"**
3. You'll get a URL like:
 
```
https://luminara-backend.up.railway.app
```
 
---
 
### Frontend → Vercel
 
#### Step 1: Add `.env` in `frontend/`
 
```env
VITE_API_URL=https://luminara-backend.up.railway.app
```
 
#### Step 2: Update API base URL in your frontend code
 
```javascript
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000"
```
 
#### Step 3: Deploy on Vercel
 
1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click **"New Project"** → import your `luminara` repo
3. Set **Root Directory** to `frontend`
4. Add env variable: `VITE_API_URL` = your Railway backend URL
5. Click **Deploy** 🚀
 
> Your app will be live at `https://luminara.vercel.app`
 
---
 
## ⚙️ How It Works
 
```
📄 User uploads PDF
        ↓
💾 Backend saves file to disk
        ↓
✂️  Background thread chunks the document
        ↓
🔢 Each chunk → embedding vector
        ↓
🗄️  Vectors stored in ChromaDB
        ↓
❓ User asks a question
        ↓
🔍 ChromaDB finds most relevant chunks (MMR search)
        ↓
🤖 Chunks + question → LLaMA 3.3 via Groq
        ↓
✨ Structured answer returned to user
```
 
---
 
## ✅ Features
 
- 📁 Upload **PDF**, **TXT**, and **CSV** files
- ⚡ Background embedding — upload returns instantly
- 🔍 **MMR retrieval** — diverse, non-redundant context
- 📝 **Markdown formatted** answers with headings and lists
- 💬 Chat history stored per session
- 🌐 CORS configured for local and production
- 🏥 Health check endpoint for Railway monitoring
 
---
 
## 👨‍💻 Built By
 
**Devang** &nbsp;·&nbsp; Built with LLaMA 3.3 &nbsp;·&nbsp; Powered by Groq &nbsp;·&nbsp; RAG Architecture
 
---
 
## 📄 License
 
MIT License — free to use, modify, and distribute.
