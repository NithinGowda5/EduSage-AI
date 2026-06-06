# EduSage AI — Multi-Document RAG Research Assistant

EduSage AI is a premium, responsive multi-document RAG (Retrieval-Augmented Generation) application designed for academic paper analysis, summary generation, and interactive document querying.

## How to Deploy to Render

Render is an excellent platform for hosting this FastAPI-based RAG application. You can deploy it directly using the pre-configured `Dockerfile` with a persistent storage disk.

### Step 1: Create a Render Web Service
1. Log in to [Render](https://render.com/).
2. Click **New +** in the top right and select **Web Service**.
3. Link your GitHub account and select your repository: `NithinGowda5/EduSage-AI`.
4. In the settings page:
   - **Name**: `edusage-ai`
   - **Environment**: Select **Docker** (Render will automatically build and run the project using the existing `Dockerfile`).
   - **Instance Type**: Select **Free** (or a paid tier if you want faster build times).

### Step 2: Configure Environment Variables
Scroll down to the **Advanced** section or go to the **Environment** tab in your Web Service settings, and add the following keys:
*   `COHERE_API_KEY`: Your Cohere API key (used to generate text embeddings when uploading PDFs).
*   `OPENROUTER_API_KEY`: Your OpenRouter API key (used to run LLM models for Q&A and reports).

*Note: Your end-users do NOT need their own API keys. The app backend securely routes all user queries through these master keys.*

### Step 3: Attach a Persistent Disk (Crucial for RAG)
Because Render's default container filesystem is ephemeral (it resets on restarts and deployments), you must attach a persistent disk to prevent your uploaded PDFs, report history, and vector databases from being wiped out:
1. In your Web Service settings page, navigate to the **Disks** section.
2. Click **Add Disk**.
3. Configure it as follows:
   - **Name**: `edusage-data`
   - **Mount Path**: `/data` (EduSage AI is pre-configured to detect `/data` and automatically write uploads and vector tables here).
   - **Size**: `1 GB` (or more based on your document collection needs).
4. Save the changes. Render will automatically redeploy the service with persistent storage mounted.

---

## Local Development Setup

To run this project locally, follow these steps:

1. Clone the repository and navigate to the directory:
   ```bash
   cd EduSage-AI
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root folder using `.env.example` as a template and enter your API keys.
4. Run the local development server:
   ```bash
   python server.py
   ```
5. Open your browser to `http://localhost:8000/`.
