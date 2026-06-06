import os
from src.retrieval import initialize_vector_db

def generate_dashboard_metrics():
    """Generates analytics and metrics for the ingested document collection."""
    total_chunks = 0
    try:
        vectorstore = initialize_vector_db()
        total_chunks = vectorstore._collection.count()
    except Exception as e:
        pass
        
    base_data_dir = "/data" if (os.path.exists("/data") or os.environ.get("SPACE_ID")) else "data"
    uploads_dir = os.path.join(base_data_dir, "uploads")
    total_docs = len(os.listdir(uploads_dir)) if os.path.exists(uploads_dir) else 0
    
    # Mock themes for demonstration. In a real system, you might run BERTopic 
    # or an LLM summarization over the parent documents to extract real themes.
    themes = [
        "Artificial Intelligence & Machine Learning",
        "Regulatory Compliance and Privacy",
        "Market Analysis and Competitor Trends",
        "Financial and Strategic Planning",
        "System Architecture and Engineering"
    ]
    
    return {
        "total_docs": total_docs,
        "total_chunks": total_chunks,
        "db_size": f"{total_chunks * 2} KB (Estimated)", 
        "themes": themes
    }
