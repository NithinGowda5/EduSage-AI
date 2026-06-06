import os
from tempfile import NamedTemporaryFile
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def load_documents_from_dir(directory_path: str) -> list[Document]:
    """Load all PDF documents from a directory."""
    documents = []
    if not os.path.exists(directory_path):
        return documents
        
    for filename in os.listdir(directory_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(directory_path, filename)
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            # Ensure metadata includes document name
            for doc in docs:
                doc.metadata["source_document"] = filename
            documents.extend(docs)
            
    return documents

def chunk_documents(documents: list[Document], parent_chunk_size=2000, child_chunk_size=400) -> tuple[list[Document], list[Document]]:
    """
    Splits documents into parent and child chunks for hierarchical retrieval.
    Returns: (parent_docs, child_docs)
    """
    # Parent splitter
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=parent_chunk_size, 
        chunk_overlap=200
    )
    # Child splitter
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=child_chunk_size, 
        chunk_overlap=50
    )
    
    parent_docs = parent_splitter.split_documents(documents)
    
    # Assign unique IDs to parents
    for i, p_doc in enumerate(parent_docs):
        p_doc.metadata["doc_id"] = f"parent_{i}"
        
    child_docs = []
    for p_doc in parent_docs:
        c_docs = child_splitter.split_documents([p_doc])
        for c in c_docs:
            c.metadata["parent_id"] = p_doc.metadata["doc_id"]
        child_docs.extend(c_docs)
        
    return parent_docs, child_docs
