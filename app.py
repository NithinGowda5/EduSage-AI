# pyrefly: ignore [missing-import]
import streamlit as st
import os
import shutil
import time
from dotenv import load_dotenv

from src.ingestion import load_documents_from_dir, chunk_documents
from src.retrieval import initialize_vector_db, save_bm25_retriever
# pyrefly: ignore [missing-import]
from langchain_community.retrievers import BM25Retriever

load_dotenv(override=True)

# Must be the first Streamlit command
st.set_page_config(page_title="Multi-Doc RAG Assistant", page_icon="📚", layout="wide", initial_sidebar_state="expanded")

# Inject Custom CSS for Premium Design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Advanced Animated Mesh Gradient Background */
    .stApp {
        background: linear-gradient(135deg, #090e17 0%, #151025 50%, #0d1117 100%);
        background-size: 200% 200%;
        animation: gradientShift 15s ease infinite;
        color: #e6edf3;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Sidebar Advanced Styling */
    section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div {
        background: rgba(18, 22, 29, 0.7);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    
    /* Headers with subtle glow */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
        text-shadow: 0px 2px 10px rgba(0,0,0,0.5);
    }
    
    h1 { font-size: 2.4rem; }
    h2 { font-size: 1.8rem; }
    h3 { font-size: 1.5rem; }
    
    /* Ultra-Premium Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #2b5fe1 0%, #4a1791 100%);
        color: #ffffff;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        box-shadow: 0 4px 15px rgba(43, 95, 225, 0.3), inset 0 1px 0 rgba(255,255,255,0.2);
    }
    
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(74, 23, 145, 0.5), inset 0 1px 0 rgba(255,255,255,0.3);
        border: 1px solid rgba(255,255,255,0.3);
        color: #ffffff;
    }
    
    .stButton>button:active {
        transform: translateY(1px) scale(0.98);
        box-shadow: 0 2px 10px rgba(74, 23, 145, 0.3);
    }
    
    /* ChatGPT-Style Chat Interface */
    /* Base Chat container */
    [data-testid="stChatMessage"] {
        border-radius: 16px;
        padding: 1.2rem;
        margin-bottom: 15px;
        border: 1px solid rgba(255,255,255,0.05);
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
    }
    
    [data-testid="stChatMessage"]:hover {
        transform: translateY(-2px);
    }
    
    /* User Message distinct style (Indigo bubble layout) */
    [data-testid="stChatMessage"]:has([data-testid="stIconUser"]) {
        background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
        border: 1px solid rgba(255,255,255,0.1);
        margin-left: 2rem; 
        border-bottom-right-radius: 4px;
    }
    
    /* Assistant Message distinct style (glassmorphic dark card) */
    [data-testid="stChatMessage"]:has(svg[title="assistant"]) {
        background: rgba(22, 27, 34, 0.6);
        backdrop-filter: blur(10px);
        border-bottom-left-radius: 4px;
        margin-right: 2rem;
    }
    
    [data-testid="stChatMessageContent"] {
        padding-top: 5px;
        line-height: 1.6;
    }
    
    /* File uploader animated dashed border */
    .stFileUploader > div:first-child {
        background: rgba(33, 38, 45, 0.5);
        border: 2px dashed #444c56;
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:first-child:hover {
        border-color: #58a6ff;
        background: rgba(88, 166, 255, 0.05);
        box-shadow: 0 0 15px rgba(88, 166, 255, 0.1);
    }
    
    /* Ultra-Premium Glass Metrics Cards */
    [data-testid="metric-container"] {
        background: rgba(33, 38, 45, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        backdrop-filter: blur(8px);
        transition: all 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        border-color: rgba(255, 255, 255, 0.2);
    }
    
    [data-testid="stMetricValue"] {
        color: #79c0ff;
        font-weight: 700;
        font-size: 2rem;
    }
    
    [data-testid="stMetricLabel"] {
        color: #8b949e;
        font-size: 1rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Hide Default Streamlit Noise */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Modern "Pill" Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background: rgba(22, 27, 34, 0.4);
        padding: 8px 12px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        margin-bottom: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: transparent;
        border-radius: 14px !important;
        padding: 0 20px;
        font-weight: 600;
        font-size: 1.05rem;
        color: #8b949e;
        transition: all 0.3s ease;
        border: none !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.08);
        color: #e6edf3;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    /* Input Fields */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background: rgba(22, 27, 34, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: #fff;
        padding: 0.75rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #58a6ff;
        box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.3);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: rgba(33, 38, 45, 0.4);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
</style>
""", unsafe_allow_html=True)

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)
os.makedirs("data/uploads", exist_ok=True)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🔑 Configuration</h2>", unsafe_allow_html=True)
    
    cohere_key = st.text_input("Cohere API Key (Required)", type="password", value=os.environ.get("COHERE_API_KEY", ""), placeholder="dIe3...")
    
    if cohere_key:
        os.environ["COHERE_API_KEY"] = cohere_key
        
    st.divider()
    
    st.markdown("<h2 style='text-align: center;'>📚 Collection</h2>", unsafe_allow_html=True)
    st.markdown("Upload individual or multiple PDFs to add them to your research library.")
    
    uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
    
    if st.button("🚀 Process Documents", use_container_width=True) and uploaded_files:
        if not os.environ.get("COHERE_API_KEY"):
            st.error("Please enter your Cohere API Key above to process documents!")
        else:
            with st.spinner("Processing files..."):
                # Save files temporarily
                for file in uploaded_files:
                    file_path = os.path.join("data/uploads", file.name)
                    with open(file_path, "wb") as f:
                        f.write(file.getbuffer())
                    st.success(f"Saved {file.name}")
                
                st.info("Parsing and chunking documents...")
                docs = load_documents_from_dir("data/uploads")
                parent_docs, child_docs = chunk_documents(docs)
                st.success(f"Created {len(parent_docs)} parent & {len(child_docs)} child chunks.")
                
                st.info("Embedding and indexing (this may take a moment)...")
                vectorstore = initialize_vector_db()
                vectorstore.add_documents(child_docs)
                
                st.info("Building BM25 keyword index...")
                bm25_retriever = BM25Retriever.from_documents(child_docs)
                save_bm25_retriever(bm25_retriever)
                
                st.success("✅ Processed successfully!")
                time.sleep(1.5)
                st.rerun()
            
    st.divider()
    
    st.subheader("Current Documents")
    # Simple list of uploaded files
    files = os.listdir("data/uploads") if os.path.exists("data/uploads") else []
    if files:
        for f in files:
            col1, col2 = st.columns([0.8, 0.2])
            with col1:
                st.markdown(f"<span style='font-size:0.95em;'>📄 {f}</span>", unsafe_allow_html=True)
            with col2:
                if st.button("✕", key=f"del_{f}", help=f"Delete {f}"):
                    try:
                        os.remove(os.path.join("data/uploads", f))
                    except:
                        pass
                    st.rerun()
    else:
        st.info("No documents in collection.")

# ----------------- MAIN AREA -----------------
st.title("Multi-Document RAG Research Assistant")
st.markdown("Interact with your uploaded knowledge base. Ask questions, generate comprehensive reports, or uncover analytics.")

tab1, tab2, tab3 = st.tabs(["💬 Chat & Q&A", "📄 Research Report", "📊 Analytics"])

with tab1:
    st.markdown("### Research Assistant Chat")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "How can I help you extract insights from your documents today?"}]

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask a research question about your documents..."):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Retrieving and Synthesizing..."):
                try:
                    from src.retrieval import get_hybrid_retriever, load_bm25_retriever, get_reranking_retriever
                    from src.generation import generate_answer
                    
                    # 1. Retrieval
                    bm25 = load_bm25_retriever()
                    if not bm25:
                        raise ValueError("No documents processed. Please upload and process documents first.")
                        
                    base_retriever = get_hybrid_retriever(bm25)
                    reranker = get_reranking_retriever(base_retriever, top_n=5)
                    
                    docs = reranker.invoke(prompt)
                    
                    # 2. Generation
                    answer = generate_answer(prompt, docs)
                    
                    st.markdown(answer)
                    
                    with st.expander("📚 View Source Documents (Citations)"):
                        for i, d in enumerate(docs):
                            source = d.metadata.get('source_document', 'Unknown')
                            page = d.metadata.get('page', 'Unknown')
                            st.markdown(f"**{i+1}. {source} (Page {page})**\n\n_{d.page_content[:300]}..._")
                            if i < len(docs) - 1:
                                st.divider()
                                
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    st.error(f"Error during search: {str(e)}")

with tab2:
    st.markdown("### Generate Research Report")
    st.info("Generate a structured Word document report based on a detailed research request.")
    
    report_query = st.text_area("Detailed Research Question / Topic Area:", height=150, placeholder="e.g. Provide a comprehensive summary of the market analysis documents, highlighting key trends and competitor strategies.")
    
    if st.button("✨ Generate Comprehensive Report"):
        if report_query:
            with st.spinner("Compiling comprehensive report. This may take a minute..."):
                try:
                    from src.retrieval import get_hybrid_retriever, load_bm25_retriever, get_reranking_retriever
                    from src.generation import generate_research_report, export_to_word
                    
                    bm25 = load_bm25_retriever()
                    base_retriever = get_hybrid_retriever(bm25)
                    reranker = get_reranking_retriever(base_retriever, top_n=10)
                    
                    docs = reranker.invoke(report_query)
                    
                    report = generate_research_report(report_query, docs)
                    st.success("✅ Report generated successfully!")
                    
                    st.markdown("#### Preview")
                    with st.container(height=400, border=True):
                        st.markdown(report)
                    
                    # Export
                    export_path = export_to_word(report)
                    with open(export_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Report (.docx)", 
                            data=f, 
                            file_name="Research_Report.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Error generating report: {str(e)}")
        else:
            st.warning("Please enter a research topic first.")

with tab3:
    st.markdown("### Knowledge Base Analytics")
    
    if st.button("🔄 Refresh Analytics"):
        with st.spinner("Analyzing collection..."):
            try:
                from src.analytics import generate_dashboard_metrics
                
                metrics = generate_dashboard_metrics()
                
                # Use cards for metrics
                st.markdown("#### Collection Metrics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric(label="📄 Total Documents", value=metrics["total_docs"])
                with col2:
                    st.metric(label="🧩 Total Vector Chunks", value=metrics["total_chunks"])
                with col3:
                    st.metric(label="💾 Est. Index Size", value=metrics.get("db_size", "Unknown"))
                
                st.divider()
                st.markdown("#### Discovered Themes & Topics ✨")
                st.caption("The following major themes were dynamically identified across your document collection:")
                
                for t in metrics["themes"]:
                    st.markdown(f"- **{t}**")
                    
            except Exception as e:
                st.error(f"Error generating analytics: {str(e)}")
