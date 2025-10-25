import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

# --- LangChain Imports (Matches your Ollama/ChromaDB setup) ---
try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter 
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_community.llms import Ollama
    from langchain_community.vectorstores import Chroma
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.chains import create_retrieval_chain
    from langchain_core.documents import Document
except ImportError:
    # This block ensures the user knows they need to run pip install -r requirements.txt
    print("\n--- ERROR: PYTHON PACKAGES MISSING ---")
    print("Please ensure you have installed all required libraries.")
    print("In your terminal, run: pip install -r requirements.txt")
    sys.exit(1)

# --- CONFIGURATION (Ollama Setup) ---
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "llama3.2:3b"  
EMBEDDING_MODEL = "mxbai-embed-large:latest" 
PDF_PATH = "csr_chat_transcript.pdf"
VECTOR_DB_PATH = "./chat_rag_db"

# --- FASTAPI SETUP ---
app = FastAPI(title="Local RAG Chatbot API (Ollama/Chroma)")

# Critical: Allows the index.html file (running locally) to talk to the server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RAG_CHAIN = None 

# --- MOCK PDF CONTENT (Fallback if PDF is missing/corrupt) ---
MOCK_CHAT_CONTENT = [
    "--- CSR Chat Transcript - Order 78901 ---\n",
    "Client: My order 78901 was supposed to arrive today, but the tracking shows 'Delayed'. What is the new estimated delivery date (EDD)?",
    "CSR: I apologize for the delay. Order 78901 for the Nebula 5000 is currently stuck in transit at the Chicago hub due to weather. The revised EDD is now Saturday, 3 days from now.",
    "Client: Is there any way to expedite it? I need it for a presentation on Friday.",
    "CSR: Unfortunately, standard shipping cannot be expedited once in this stage. However, I can offer you a 15% discount on your next accessory purchase as compensation for the inconvenience.",
    "Client: What about the warranty? Does this delay affect the 1-year guarantee I purchased?",
    "CSR: Not at all. The 1-year guarantee starts upon successful delivery, which will be Saturday. I have documented the delay under ticket #RAG-2025.",
]

def load_documents(path: str) -> List[Document]:
    """Loads a PDF document or uses mock content if the file is not found."""
    if os.path.exists(path):
        try:
            # Load from the real PDF file
            loader = PyPDFLoader(path)
            documents = loader.load()
            return documents
        except Exception:
            # Fallback to mock content if PDF is corrupted
            return [Document(page_content="\n".join(MOCK_CHAT_CONTENT), metadata={"source": "mock_chat_transcript_fallback"})]
    else:
        # Fallback to mock content if PDF is missing
        return [Document(page_content="\n".join(MOCK_CHAT_CONTENT), metadata={"source": "mock_chat_transcript_missing"})]

def setup_rag_system():
    """Sets up the RAG system: loads data, creates chunks, and initializes the Vector Store and Chain."""
    
    docs = load_documents(PDF_PATH)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(docs)

    # Initialize Ollama Components
    llm = Ollama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL)
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)

    # Create or Load Vector Store (ChromaDB)
    vector_store = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=VECTOR_DB_PATH
    )
    retriever = vector_store.as_retriever()
    
    system_prompt = (
        "You are an expert Chat Transcript Analyst. "
        "Your task is to answer user questions based STRICTLY on the provided chat excerpts. "
        "Do not invent information. If the context does not contain the answer, state that you cannot find the specific information. "
        "Always be concise and cite the source information explicitly."
        "\n\nContext: {context}"
    )
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    return retrieval_chain

class QueryRequest(BaseModel):
    query: str

@app.on_event("startup")
async def startup_event():
    """Initializes the RAG chain when the FastAPI server starts."""
    global RAG_CHAIN
    print("\n[SERVER] Initializing RAG System...")
    try:
        RAG_CHAIN = setup_rag_system()
        print(f"[SERVER] RAG System Ready. Models: {LLM_MODEL} & {EMBEDDING_MODEL}.")
        print(f"[SERVER] Data loaded from: {PDF_PATH}")
    except Exception as e:
        print(f"[SERVER] CRITICAL ERROR during RAG initialization. Check if Ollama is running and models are pulled: {e}")
        # Stop the server startup if RAG fails (likely Ollama connection issue)
        raise HTTPException(status_code=500, detail="RAG system failed to initialize. Check Ollama status and model availability.")

@app.post("/query")
async def query_chatbot(request: QueryRequest):
    """API endpoint to receive user queries and return RAG responses."""
    if RAG_CHAIN is None:
        raise HTTPException(status_code=503, detail="RAG System not ready or failed to initialize.")
    
    try:
        # Use asynchronous invocation for non-blocking I/O
        response = await RAG_CHAIN.ainvoke({"input": request.query})
        
        # Format the response for the frontend
        return {
            "answer": response["answer"],
            "sources": [doc.metadata.get('source', 'Unknown') for doc in response["context"]],
            "context_snippets": [doc.page_content[:200] + "..." for doc in response["context"]] # For debugging/display
        }
    except Exception as e:
        # Check for connection errors specifically related to Ollama
        if "ConnectionError" in str(e) or "Max retries exceeded" in str(e):
            raise HTTPException(status_code=504, detail="Could not connect to Ollama. Is the Ollama server running and the models pulled?")
        
        raise HTTPException(status_code=500, detail=f"Internal RAG processing error: {e}")

if __name__ == "__main__":
    # Start the server on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
