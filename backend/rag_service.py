import os
import glob as glob_module
from typing import List, Tuple

from langchain_community.document_loaders import PyPDFLoader, TextLoader, CSVLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()


class RAGService:
    def __init__(self, data_path: str = "../data", chroma_path: str = "../chroma_db"):
        self.data_path   = data_path
        self.chroma_path = chroma_path

        os.makedirs(self.data_path, exist_ok=True)

        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"batch_size": 64, "normalize_embeddings": True},
        )

        self.llm = self._init_llm()
        self.vector_store = self._init_vector_store()

    def _init_llm(self):
        return ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0.4,
            max_tokens=4096,
        )

    def _init_vector_store(self):
        db_file = os.path.join(self.chroma_path, "chroma.sqlite3")
        if os.path.exists(self.chroma_path) and os.path.exists(db_file):
            return Chroma(
                persist_directory=self.chroma_path,
                embedding_function=self.embeddings,
            )
        docs   = self._load_all_documents()
        chunks = self._split(docs)
        if chunks:
            return Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=self.chroma_path,
            )
        return Chroma(
            persist_directory=self.chroma_path,
            embedding_function=self.embeddings,
        )

    def _load_all_documents(self):
        docs = []
        if not os.path.exists(self.data_path):
            return docs

        try:
            docs.extend(
                DirectoryLoader(self.data_path, glob="**/*.txt", loader_cls=TextLoader).load()
            )
        except Exception as e:
            print(f"TXT load warning: {e}")

        try:
            docs.extend(
                DirectoryLoader(self.data_path, glob="**/*.pdf", loader_cls=PyPDFLoader).load()
            )
        except Exception as e:
            print(f"PDF load warning: {e}")

        for csv_path in glob_module.glob(
            os.path.join(self.data_path, "**/*.csv"), recursive=True
        ):
            try:
                docs.extend(CSVLoader(file_path=csv_path, encoding="utf-8").load())
            except Exception as e:
                print(f"CSV load warning {csv_path}: {e}")

        return docs

    def _load_file(self, file_path: str):
        if file_path.endswith(".pdf"):
            return PyPDFLoader(file_path).load()
        if file_path.endswith(".txt"):
            return TextLoader(file_path).load()
        if file_path.endswith(".csv"):
            return CSVLoader(file_path=file_path, encoding="utf-8").load()
        raise ValueError(f"Unsupported file type: {file_path}")

    def _split(self, docs, chunk_size=800, chunk_overlap=150):
        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        ).split_documents(docs)

    def embed_document(self, file_path: str):
        docs   = self._load_file(file_path)
        chunks = self._split(docs)
        if chunks:
            self.vector_store.add_documents(chunks)
        print(f"[embed] Done: {file_path} ({len(chunks)} chunks)")

    def query(self, question: str) -> Tuple[str, List[str]]:
        retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 8,
                "fetch_k": 20,
                "lambda_mult": 0.6,
            },
        )

        prompt = PromptTemplate.from_template(
            """You are Luminara, an expert AI research analyst. Your job is to give the most
complete, accurate, and well-structured answer possible using the provided context.

## Instructions
- **Be thorough**: Cover all relevant aspects found in the context. Do not cut answers short.
- **Structure clearly**: Use markdown headings (##, ###), bullet points (-), numbered lists,
  bold key terms, and tables where applicable.
- **Cite specifics**: Include exact figures, dates, names, and quotes from the context.
- **Multi-part questions**: Address every part of the question separately.
- **If data is missing**: Say exactly which part of the question the documents do not cover.
  Do not guess or hallucinate information.

---

**Question:** {question}

**Context from documents:**
{context}

---

Provide a detailed, comprehensive answer below:"""
        )

        def format_docs(docs):
            parts = []
            for i, doc in enumerate(docs, 1):
                src = doc.metadata.get("source", "unknown")
                parts.append(f"[Chunk {i} · {os.path.basename(src)}]\n{doc.page_content}")
            return "\n\n---\n\n".join(parts)

        chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        answer = chain.invoke(question)

        source_docs = retriever.invoke(question)
        sources = [doc.page_content[:300] for doc in source_docs]

        return answer, sources