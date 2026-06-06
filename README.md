---
title: EduSage AI
emoji: ⚡
colorFrom: purple
colorTo: orange
sdk: docker
app_port: 7860
pinned: false
---

# EduSage AI — Multi-Document RAG Research Assistant

EduSage AI is a premium, responsive multi-document RAG (Retrieval-Augmented Generation) application designed for academic paper analysis, summary generation, and interactive document querying.

## How to Deploy to Hugging Face Spaces

1. Create a new Space on [Hugging Face Spaces](https://huggingface.co/new-space).
2. Provide a name and set the Space SDK to **Docker**.
3. Push/Commit the files in this project directory to your Hugging Face Space repository.
4. **Persistent Storage (Highly Recommended)**:
   - In your Space settings tab, attach a **Persistent Storage** tier (e.g. the free Dev tier or any storage size).
   - Once attached, Hugging Face mounts a persistent network storage drive at `/data`. EduSage AI automatically detects this directory and routes all PDF uploads, Chroma DB chunks, and report history to `/data/` so that your library persists across Space rebuilds or restarts!
5. **Add Secrets / Environment Variables**:
   - In your Hugging Face Space settings under "Variables and secrets", add:
     - `COHERE_API_KEY`: (Secret) Your Cohere API key (needed to calculate vector embeddings when uploading PDFs).
     - `OPENROUTER_API_KEY`: (Secret) Your OpenRouter API key (needed to call LLM models for Q&A and reports).
