import os
from typing import List
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Load environment variables (like GROQ_API_KEY)
load_dotenv()

DATA_PATH = "data"
CHROMA_PATH = "chroma_db"

def initialize_groq():
    return ChatGroq(
        model_name="llama-3.3-70b-versatile",
        temperature=0.7,
        max_tokens=500
    )

def load_documents():
    """Loads text and PDF documents from the data directory."""
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
        print(f"Created '{DATA_PATH}' directory. Please add some .txt or .pdf files here.")
        return []

    print(f"Loading documents from {DATA_PATH}...")
    documents = []
    
    # Load Text files
    txt_loader = DirectoryLoader(DATA_PATH, glob="**/*.txt", loader_cls=TextLoader)
    documents.extend(txt_loader.load())
    
    # Load PDF files
    pdf_loader = DirectoryLoader(DATA_PATH, glob="**/*.pdf", loader_cls=PyPDFLoader)
    documents.extend(pdf_loader.load())
    
    print(f"Loaded {len(documents)} documents.")
    return documents

def split_documents(documents):
    """Splits documents into smaller chunks."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split documents into {len(chunks)} chunks.")
    return chunks

def build_vector_store(chunks):
    """Builds and returns a Chroma vector store from document chunks."""
    if not chunks:
        print("No document chunks to embed. Returning existing vector store if available.")
        # If the DB already exists, we can still load it
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        return Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)
        
    print("Generating embeddings and building vector store (this might take a moment)...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    print(f"Vector store saved to {CHROMA_PATH}")
    return vector_store

def create_rag_chain(vector_store, llm):
    """Creates the retrieval-augmented generation chain."""
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    # Define how context is mapped to the prompt
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    template = """You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer based on the context, just say that you don't know. 
Use three sentences maximum and keep the answer concise.

Question: {question} 

Context: {context} 

Answer:"""
    prompt = PromptTemplate.from_template(template)
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def run_interactive_loop():
    """Runs a loop to wait for user queries."""
    # 1. Initialize components
    llm = initialize_groq()
    
    # 2. Load and process documents
    docs = load_documents()
    chunks = split_documents(docs)
    
    # 3. Build Vector Store
    vector_store = build_vector_store(chunks)
    
    if not os.path.exists(CHROMA_PATH) and len(chunks) == 0:
        print("\n[WARNING] No documents found and no vector store exists.")
        print("Please place some .txt or .pdf files in the 'data' directory and rerun.")
        return
        
    # 4. Create pipeline
    rag_chain = create_rag_chain(vector_store, llm)
    
    print("\n" + "="*50)
    print("RAG Pipeline is ready! Ask your questions.")
    print("Type 'exit' or 'quit' to stop.")
    print("="*50 + "\n")
    
    # 5. Question loop
    while True:
        try:
            query = input("Ask a question: ")
        except (KeyboardInterrupt, EOFError):
            break
            
        if query.lower() in ["exit", "quit", "q"]:
            break
            
        if not query.strip():
            continue
            
        print("Thinking...")
        try:
            response = rag_chain.invoke(query)
            print("\nResponse:")
            print("-" * 50)
            print(response)
            print("-" * 50, "\n")
        except Exception as e:
            print(f"An error occurred: {e}\n")

if __name__ == "__main__":
    run_interactive_loop()
