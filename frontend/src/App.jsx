import { useState, useEffect, useRef, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './index.css';

// ── Icons ──
const LogoIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 2L2 7l10 5 10-5-10-5z"/>
    <path d="M2 17l10 5 10-5"/>
    <path d="M2 12l10 5 10-5"/>
  </svg>
);

const UploadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
    <polyline points="17 8 12 3 7 8"/>
    <line x1="12" y1="3" x2="12" y2="15"/>
  </svg>
);

const SendIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13"/>
    <polygon points="22 2 15 22 11 13 2 9 22 2"/>
  </svg>
);

const DocumentIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
    <polyline points="14 2 14 8 20 8"/>
  </svg>
);

const UserIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
    <circle cx="12" cy="7" r="4"/>
  </svg>
);

const TrashIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="3 6 5 6 21 6"/>
    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
  </svg>
);

const CopyIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
  </svg>
);

const CheckIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

// ── CopyButton ──
function CopyButton({ text }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try { await navigator.clipboard.writeText(text); } catch {}
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button className={`copy-btn ${copied ? 'copied' : ''}`} onClick={copy}>
      {copied ? <CheckIcon /> : <CopyIcon />}
      {copied ? 'Copied' : 'Copy'}
    </button>
  );
}

// ── FileStatusBadge ──
function FileStatusBadge({ filename, onReady }) {
  const [status, setStatus] = useState('processing');

  useEffect(() => {
    if (status === 'ready') return;
    const id = setInterval(async () => {
      try {
        const res  = await fetch(`${API_URL}/status/${encodeURIComponent(filename)}`);
        const data = await res.json();
        setStatus(data.status);
        if (data.status === 'ready') {
          clearInterval(id);
          onReady && onReady(filename);
        }
      } catch {}
    }, 2000);
    return () => clearInterval(id);
  }, [filename, status, onReady]);

  if (status === 'ready') return <span className="file-badge ready">Ready</span>;
  if (status?.startsWith('error')) return <span className="file-badge error">Error</span>;
  return <span className="file-badge processing">Embedding…</span>;
}

// ── API URL ──
const API_URL = import.meta.env.VITE_API_URL || "";

// ── App ──
function App() {
  const [messages, setMessages]         = useState([]);
  const [inputValue, setInputValue]     = useState("");
  const [isLoading, setIsLoading]       = useState(false);
  const [file, setFile]                 = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [isUploading, setIsUploading]   = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const messagesEndRef = useRef(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const handleFileChange = (e) => { if (e.target.files?.[0]) { setFile(e.target.files[0]); setUploadStatus(null); } };
  const removeFile = (e) => { e.preventDefault(); setFile(null); setUploadStatus(null); const inp = document.getElementById('file-upload'); if(inp) inp.value=""; };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setUploadStatus(null);
    const fd = new FormData();
    fd.append("file", file);
    try {
      const res = await fetch(`${API_URL}/upload`, { method: "POST", body: fd });
      const data = await res.json();
      if (res.ok) {
        setUploadStatus({ type: 'success', message: `"${file.name}" saved. Embedding in background…` });
        const name = file.name;
        setUploadedFiles(prev => [...prev.filter(f => f.name!==name), { name, status:'processing' }]);
        setFile(null);
        const inp = document.getElementById('file-upload'); if(inp) inp.value="";
      } else { setUploadStatus({ type: 'error', message: data.detail || 'Upload failed.' }); }
    } catch { setUploadStatus({ type:'error', message:'Cannot reach backend. Is the server running?' }); }
    finally { setIsUploading(false); }
  };

  const handleFileReady = useCallback((name) => {
    setUploadedFiles(prev => prev.map(f => f.name===name ? { ...f, status:'ready'} : f));
  }, []);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;
    const text = inputValue;
    setMessages(prev => [...prev, { role:'user', text }]);
    setInputValue("");
    setIsLoading(true);
    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type":"application/json" },
        body: JSON.stringify({ query:text }),
      });
      const data = await res.json();
      if(res.ok) setMessages(prev => [...prev, { role:'ai', text:data.answer, sources:data.sources||[] }]);
      else setMessages(prev => [...prev, { role:'ai', text:`**Error:** ${data.detail||'Something went wrong.'}` }]);
    } catch { setMessages(prev => [...prev, { role:'ai', text:'**Network Error:** Could not reach the backend.' }]); }
    finally { setIsLoading(false); }
  };

  const handleKeyDown = (e) => { if(e.key==='Enter' && !e.shiftKey) handleSend(e); };
  const userQueries = messages.filter(m => m.role==='user');

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon"><LogoIcon /></div>
          <div className="brand-text">
            <span className="brand-name">Luminara</span>
            <span className="brand-tagline">Research Assistant</span>
          </div>
        </div>

        {/* Upload Section */}
        <div className="sidebar-section">
          <span className="section-label">Knowledge Base</span>
          <label className={`upload-area ${file?'has-file':''}`}>
            <input id="file-upload" type="file" accept=".pdf,.txt,.csv" onChange={handleFileChange} style={{ display:'none' }} />
            {file ? (
              <div className="file-ready-state">
                <div className="file-ready-icon"><DocumentIcon /></div>
                <div className="file-name" title={file.name}>{file.name}</div>
                <button className="remove-file-btn" onClick={removeFile} title="Remove"><TrashIcon /></button>
              </div>
            ) : (
              <>
                <div className="upload-icon-wrap"><UploadIcon /></div>
                <div className="upload-text">Click or drop a file</div>
                <div className="upload-help">PDF, TXT or CSV</div>
              </>
            )}
          </label>
          <button className={`upload-btn ${isUploading?'loading':''}`} onClick={handleUpload} disabled={!file || isUploading}>
            {isUploading ? <>Uploading…</> : 'Add to Knowledge Base'}
          </button>
          {uploadStatus && <div className={`status-message status-${uploadStatus.type}`}>{uploadStatus.message}</div>}

          {/* Indexed Files */}
          {uploadedFiles.length>0 && (
            <div className="file-list">
              <span className="file-list-label">Indexed files</span>
              {uploadedFiles.map(f=>(
                <div key={f.name} className="file-list-item">
                  <DocumentIcon />
                  <span className="file-list-name" title={f.name}>{f.name}</span>
                  <FileStatusBadge filename={f.name} onReady={handleFileReady} />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Query History */}
        <div className="history-section">
          <span className="section-label">Recent Queries</span>
          {userQueries.length===0 ? <div className="empty-history">No queries yet.</div> :
            <div className="history-scroll">{userQueries.slice().reverse().map((msg,i)=><div key={i} className="history-item">{msg.text}</div>)}</div>}
        </div>
      </aside>

      {/* Chat */}
      <main className="chat-container">
        <div className="chat-header">
          <div><div className="chat-title">Chat</div><div className="chat-subtitle">Ask questions about your documents</div></div>
          <div className="status-indicator"><span className="pulse-dot" />Connected</div>
        </div>

        <div className="messages-area">
          {messages.length===0 && !isLoading && (
            <div className="empty-state">
              <div className="empty-icon"><LogoIcon /></div>
              <h2>How can I help you today?</h2>
              <p>Upload a document, wait for it to show <strong>Ready</strong>, then ask a question.</p>
            </div>
          )}
          {messages.map((msg,idx)=>(
            <div key={idx} className={`message-wrapper ${msg.role}`}>
              <div className={`avatar ${msg.role}`}>{msg.role==='user'?<UserIcon />:'L'}</div>
              <div className={`message-content ${msg.role}`}>
                {msg.role==='user' ? <div className="user-text">{msg.text}</div> :
                  <>
                    <div className="ai-answer-header"><span className="ai-label">Luminara</span><CopyButton text={msg.text} /></div>
                    <div className="markdown-content"><ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown></div>
                  </>}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="message-wrapper ai">
              <div className="avatar ai">L</div>
              <div className="message-content ai typing-content">
                <div className="typing-indicator"><div className="typing-dot"/><div className="typing-dot"/><div className="typing-dot"/></div>
                <div className="typing-text">Searching and analysing documents…</div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <form className="input-form" onSubmit={handleSend}>
            <textarea
              className="chat-input"
              value={inputValue}
              onChange={e=>setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question… (Enter to send, Shift+Enter for new line)"
              disabled={isLoading} rows={1} autoFocus
            />
            <button type="submit" className={`send-btn ${inputValue.trim()?'active':''}`} disabled={!inputValue.trim() || isLoading}><SendIcon /></button>
          </form>
          <div className="input-footer">
            Luminara bases its answers on your documents. Verify critical info. <br/>Powered by <strong>Devang</strong> · Built with <strong>LLaMA 3.3</strong> · RAG powered
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;