# EduSage AI — Multi-Document RAG Research Assistant

EduSage AI is a premium, responsive multi-document RAG (Retrieval-Augmented Generation) application designed for academic paper analysis, summary generation, and interactive document querying. It bridges the gap between vast static document libraries and dynamic, cited knowledge synthesis.

## Core Features

- **📂 Multi-Document Library Ingestion**: Upload, process, and chunk multiple PDF research papers simultaneously into a structured vector database.
- **🔍 Hybrid Semantic Retrieval**: Combines semantic dense vector search with lexical keyword matching (BM25) to prevent domain vocabulary loss and ensure maximum document recall.
- **⚡ Advanced Reranking Pipeline**: Uses a Cohere Reranker to grade the top candidate chunks, feeding only the absolute highest relevance context into the LLM synthesis window.
- **✍️ Publication-Ready Report Generation**: Generates comprehensive research reports—complete with introduction, cross-document analysis, contradiction detection, and explicit inline citations.
- **📊 Analytics Dashboard**: Visualizes collection scale, document coverage, and automatically extracts overarching thematic concepts.
- **🔄 Rolling Slide Navigation**: A fluid, responsive UI utilizing rolling 3D card transition animations for seamless view transitions.
- **🌓 Dual-Theme Support**: Features complete day and night themes with custom visual optimization for all cards, assets, and icons.

## Architecture

1. **Extraction**: Hierarchical PDF processing and text extraction.
2. **Indexing**: Split-strategy chunking indexed across semantic vector stores and lexical databases.
3. **Retrieval**: Parallel semantic & keyword search merged with Reciprocal Rank Fusion (RRF).
4. **Refinement**: Dense reranking to maximize context density.
5. **Synthesis**: LLM generation with strict citation verification rules.
