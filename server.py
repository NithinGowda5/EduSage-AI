import os
import shutil
import time
from typing import List, Optional
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, UploadFile, File, HTTPException, Body
# pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse, JSONResponse
# pyrefly: ignore [missing-import]
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Import existing modules
from src.ingestion import load_documents_from_dir, chunk_documents
from src.retrieval import (
    initialize_vector_db,
    save_bm25_retriever,
    load_bm25_retriever,
    get_hybrid_retriever,
    get_reranking_retriever
)
from src.generation import generate_answer, generate_research_report, export_to_word
from src.analytics import generate_dashboard_metrics

# Load environment variables
load_dotenv(override=True)

app = FastAPI(
    title="Multi-Document RAG Research Assistant API",
    description="Backend API powering the responsive premium HTML/CSS/JS frontend."
)

# Ensure data directories exist
def get_base_data_dir() -> str:
    if os.path.exists("/data") or os.environ.get("SPACE_ID"):
        return "/data"
    return "data"

BASE_DATA_DIR = get_base_data_dir()
UPLOADS_DIR = os.path.join(BASE_DATA_DIR, "uploads")
os.makedirs(BASE_DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# ----------------- ENVIRONMENT PERSISTENCE -----------------

def update_env_file(key: str, value: str):
    env_path = ".env"
    lines = []
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            lines = f.readlines()
    
    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f'{key}="{value}"\n'
            found = True
            break
    if not found:
        lines.append(f'{key}="{value}"\n')
        
    with open(env_path, "w") as f:
        f.writelines(lines)

# ----------------- PYDANTIC SCHEMAS -----------------

class ConfigSchema(BaseModel):
    cohere_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    preferred_provider: Optional[str] = "cohere"
    openrouter_model: Optional[str] = "meta-llama/llama-3-8b-instruct:free"

class ChatQuerySchema(BaseModel):
    message: str

class ReportQuerySchema(BaseModel):
    query: str

# ----------------- API ENDPOINTS -----------------

@app.get("/api/config")
async def get_config():
    """Check the set configurations."""
    return {
        "cohere_key_set": bool(os.environ.get("COHERE_API_KEY")),
        "openrouter_key_set": bool(os.environ.get("OPENROUTER_API_KEY")),
        "preferred_provider": os.environ.get("PREFERRED_PROVIDER", "cohere"),
        "openrouter_model": os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3-8b-instruct:free")
    }

@app.post("/api/config")
async def set_config(data: ConfigSchema):
    """Set the API Keys and configurations in the environment and save to .env."""
    if data.cohere_api_key is not None:
        val = data.cohere_api_key.strip()
        os.environ["COHERE_API_KEY"] = val
        update_env_file("COHERE_API_KEY", val)
        
    if data.openrouter_api_key is not None:
        val = data.openrouter_api_key.strip()
        os.environ["OPENROUTER_API_KEY"] = val
        update_env_file("OPENROUTER_API_KEY", val)
        
    if data.preferred_provider is not None:
        val = data.preferred_provider.strip()
        os.environ["PREFERRED_PROVIDER"] = val
        update_env_file("PREFERRED_PROVIDER", val)
        
    if data.openrouter_model is not None:
        val = data.openrouter_model.strip()
        os.environ["OPENROUTER_MODEL"] = val
        update_env_file("OPENROUTER_MODEL", val)
        
    return {"message": "Configuration updated successfully."}

@app.get("/api/documents")
async def list_documents():
    """List all ingested PDF document filenames."""
    if not os.path.exists(UPLOADS_DIR):
        return []
    return [f for f in os.listdir(UPLOADS_DIR) if f.endswith(".pdf")]

@app.post("/api/documents/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload PDF files and trigger RAG ingestion & indexing."""
    if not os.environ.get("COHERE_API_KEY"):
        raise HTTPException(
            status_code=400, 
            detail="Cohere API Key is not configured. Please set it in the sidebar."
        )
    
    saved_files = []
    try:
        # 1. Save uploaded files to data/uploads
        for file in files:
            if not file.filename.endswith(".pdf"):
                continue
            
            file_path = os.path.join(UPLOADS_DIR, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            saved_files.append(file.filename)
            
        if not saved_files:
            raise HTTPException(status_code=400, detail="No valid PDF files were uploaded.")
            
        # 2. Run ingestion & chunking
        docs = load_documents_from_dir(UPLOADS_DIR)
        if not docs:
            raise HTTPException(status_code=500, detail="Ingestion failed: No pages loaded from PDFs.")
            
        parent_docs, child_docs = chunk_documents(docs)
        
        # 3. Add to vector store
        vectorstore = initialize_vector_db()
        vectorstore.add_documents(child_docs)
        
        # 4. Build and save BM25 keyword index
        bm25_retriever = BM25Retriever = None
        try:
            # pyrefly: ignore [missing-import]
            from langchain_community.retrievers import BM25Retriever
            bm25_retriever = BM25Retriever.from_documents(child_docs)
            save_bm25_retriever(bm25_retriever)
        except Exception as bm_err:
            print(f"BM25 build failed: {bm_err}")
            
        return {
            "message": f"Successfully processed {len(saved_files)} documents. Created {len(parent_docs)} parent and {len(child_docs)} child chunks.",
            "processed_files": saved_files
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")

@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    """Delete a document from the uploads library."""
    file_path = os.path.join(UPLOADS_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    
    try:
        os.remove(file_path)
        # Note: In a production DB we would rebuild Chroma collection or delete specific IDs.
        # For simplicity, we just delete the file. Re-processing other documents will refresh the index.
        # If no documents are left, we can clean index or let analytics know.
        
        # Re-run ingestion on remaining documents if any, to refresh BM25
        remaining = [f for f in os.listdir(UPLOADS_DIR) if f.endswith(".pdf")]
        if remaining:
            docs = load_documents_from_dir(UPLOADS_DIR)
            if docs:
                parent_docs, child_docs = chunk_documents(docs)
                vectorstore = initialize_vector_db()
                # Clear and re-populate is standard for local prototypes, or let it accumulate.
                # Here we just refresh BM25
                try:
                    # pyrefly: ignore [missing-import]
                    from langchain_community.retrievers import BM25Retriever
                    bm25_retriever = BM25Retriever.from_documents(child_docs)
                    save_bm25_retriever(bm25_retriever)
                except:
                    pass
        else:
            # Clean up BM25 pkl and Chroma if empty
            bm25_file = os.path.join(BASE_DATA_DIR, "bm25_store.pkl")
            if os.path.exists(bm25_file):
                os.remove(bm25_file)
                
        return {"message": f"Deleted {filename} successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")

@app.post("/api/chat")
async def chat_query(data: ChatQuerySchema):
    """Perform hybrid search, rerank, and answer the user query."""
    provider = os.environ.get("PREFERRED_PROVIDER", "cohere")
    if provider == "cohere" and not os.environ.get("COHERE_API_KEY"):
        raise HTTPException(status_code=400, detail="Cohere API Key not configured.")
    elif provider == "openrouter" and not os.environ.get("OPENROUTER_API_KEY"):
        raise HTTPException(status_code=400, detail="OpenRouter API Key not configured.")
        
    try:
        # Load BM25 retriever
        bm25 = load_bm25_retriever()
        if not bm25:
            raise HTTPException(
                status_code=400, 
                detail="No documents ingested. Please upload and process documents first."
            )
            
        # Get hybrid retriever and apply reranking
        base_retriever = get_hybrid_retriever(bm25)
        reranker = get_reranking_retriever(base_retriever, top_n=5)
        
        # Invoke retrieval
        docs = reranker.invoke(data.message)
        
        # Generate Answer
        answer = generate_answer(data.message, docs)
        
        # Format Citations for Frontend
        citations = []
        for d in docs:
            citations.append({
                "source": d.metadata.get("source_document", "Unknown"),
                "page": d.metadata.get("page", "Unknown"),
                "text": d.page_content[:250] + "..." if len(d.page_content) > 250 else d.page_content
            })
            
        return {
            "answer": answer,
            "citations": citations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.post("/api/report")
async def generate_report(data: ReportQuerySchema):
    """Generate a structured Markdown report and compile a downloadble Word .docx."""
    provider = os.environ.get("PREFERRED_PROVIDER", "cohere")
    if provider == "cohere" and not os.environ.get("COHERE_API_KEY"):
        raise HTTPException(status_code=400, detail="Cohere API Key not configured.")
    elif provider == "openrouter" and not os.environ.get("OPENROUTER_API_KEY"):
        raise HTTPException(status_code=400, detail="OpenRouter API Key not configured.")
        
    try:
        bm25 = load_bm25_retriever()
        if not bm25:
            raise HTTPException(
                status_code=400, 
                detail="No documents ingested. Please upload and process documents first."
            )
            
        base_retriever = get_hybrid_retriever(bm25)
        reranker = get_reranking_retriever(base_retriever, top_n=10)
        
        docs = reranker.invoke(data.query)
        
        # Generate report
        report = generate_research_report(data.query, docs)
        
        # Export to docx
        filename = f"Research_Report_{int(time.time())}.docx"
        export_path = export_to_word(report, filename=filename)
        
        return {
            "report": report,
            "filename": filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation error: {str(e)}")

@app.get("/api/report/download")
async def download_report(filename: str):
    """Download the generated report .docx file."""
    file_path = os.path.join(BASE_DATA_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Requested report file does not exist.")
        
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@app.get("/api/analytics")
async def get_analytics():
    """Retrieve metrics & dynamically identified themes for the collection."""
    try:
        metrics = generate_dashboard_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")

# Serve static frontend files
# NOTE: This must be mounted last so that it does not intercept API routes
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    # Disable reload on production/Hugging Face container
    is_prod = bool(os.environ.get("SPACE_ID"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=not is_prod)
