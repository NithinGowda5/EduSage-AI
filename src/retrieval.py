import os
import pickle

from langchain_chroma import Chroma
# pyrefly: ignore [missing-import]
from langchain_cohere import CohereEmbeddings
# pyrefly: ignore [missing-import]
from langchain_community.retrievers import BM25Retriever

# pyrefly: ignore [missing-import]
from langchain_classic.retrievers import (
    EnsembleRetriever,
    ContextualCompressionRetriever,
    ParentDocumentRetriever,
)

# pyrefly: ignore [missing-import]
from langchain_classic.storage import LocalFileStore

# pyrefly: ignore [missing-import]
from langchain_cohere import CohereRerank


# ---------------------------------------------------
# PATHS
# ---------------------------------------------------

def get_base_data_dir() -> str:
    if os.path.exists("/data") or os.environ.get("SPACE_ID"):
        return "/data"
    return "data"

BASE_DATA_DIR = get_base_data_dir()
VECTOR_DB_DIR = os.path.join(BASE_DATA_DIR, "chroma_db")
PARENT_STORE_DIR = os.path.join(BASE_DATA_DIR, "parent_store")
BM25_STORE_FILE = os.path.join(BASE_DATA_DIR, "bm25_store.pkl")

# Create directories
os.makedirs(VECTOR_DB_DIR, exist_ok=True)
os.makedirs(PARENT_STORE_DIR, exist_ok=True)

# ---------------------------------------------------
# EMBEDDINGS
# ---------------------------------------------------

def get_embeddings():
    return CohereEmbeddings(model="embed-english-v3.0")

# ---------------------------------------------------
# VECTOR DATABASE
# ---------------------------------------------------

def initialize_vector_db():

    embeddings = get_embeddings()

    vectorstore = Chroma(
        collection_name="rag_collection",
        embedding_function=embeddings,
        persist_directory=VECTOR_DB_DIR,
    )

    return vectorstore

# ---------------------------------------------------
# PARENT DOCUMENT RETRIEVER
# ---------------------------------------------------

def setup_parent_document_retriever():

    vectorstore = initialize_vector_db()

    store = LocalFileStore(PARENT_STORE_DIR)

    return vectorstore, store

# ---------------------------------------------------
# HYBRID RETRIEVER
# ---------------------------------------------------

def get_hybrid_retriever(bm25_retriever=None):

    vectorstore = initialize_vector_db()

    dense_retriever = vectorstore.as_retriever(
        search_kwargs={"k": 10}
    )

    # Hybrid Search
    if bm25_retriever is not None:

        ensemble_retriever = EnsembleRetriever(
            retrievers=[
                bm25_retriever,
                dense_retriever
            ],
            weights=[0.5, 0.5],
        )

        return ensemble_retriever

    return dense_retriever

# ---------------------------------------------------
# RERANKING RETRIEVER
# ---------------------------------------------------

def get_reranking_retriever(
    base_retriever,
    top_n=5
):

    cohere_api_key = os.environ.get("COHERE_API_KEY")

    if not cohere_api_key:
        print(
            "Warning: COHERE_API_KEY not found. "
            "Skipping reranking."
        )
        return base_retriever

    compressor = CohereRerank(
        cohere_api_key=cohere_api_key,
        model="rerank-english-v3.0",
        top_n=top_n,
    )

    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever,
    )

    return compression_retriever

# ---------------------------------------------------
# SAVE BM25 RETRIEVER
# ---------------------------------------------------

def save_bm25_retriever(retriever):

    try:
        with open(BM25_STORE_FILE, "wb") as f:
            pickle.dump(retriever, f)

        print("BM25 retriever saved successfully.")

    except Exception as e:
        print(f"Error saving BM25 retriever: {e}")

# ---------------------------------------------------
# LOAD BM25 RETRIEVER
# ---------------------------------------------------

def load_bm25_retriever():

    if not os.path.exists(BM25_STORE_FILE):
        return None

    try:
        with open(BM25_STORE_FILE, "rb") as f:
            retriever = pickle.load(f)

        print("BM25 retriever loaded successfully.")

        return retriever

    except Exception as e:
        print(f"Error loading BM25 retriever: {e}")
        return None