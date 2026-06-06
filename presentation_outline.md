# Presentation Slides - Multi-Document RAG

**Slide 1: Title Slide**
- Project Title: Multi-Document RAG Research Assistant
- Subtitle: Bridging the gap between vast libraries and instant insights

**Slide 2: The Problem**
- Synthesizing information across dozens of PDFs is slow.
- Existing search engines only find keywords, missing context.

**Slide 3: Our Solution**
- A sophisticated RAG pipeline combining Dense and Keyword search.
- Generates publication-ready reports with exact citations.

**Slide 4: Architecture Overview**
- Visual diagram: PDF -> Chunking -> ChromaDB + BM25 -> Cohere Reranker -> LLM Synthesis.

**Slide 5: Key Component - Hybrid Search**
- Why standard vector search fails (domain vocabulary loss).
- How BM25 brings it back.

**Slide 6: Key Component - Cohere Rerank**
- Taking the broad top 20 candidate chunks and finding the absolute best 5 to fit in the context window.

**Slide 7: Generation & Reporting**
- Demonstrating the output: Introduction, Cross-Document Synthesis, and Contradiction detection.
- Exporting directly to MS Word (`.docx`).

**Slide 8: Analytics Dashboard**
- Showcasing the UI tab for tracking collection scale and overarching topics.

**Slide 9: Future Roadmap**
- Expand to multi-modal (images/tables in PDFs).
- Automated literature review table generation.

**Slide 10: Conclusion & Q&A**
