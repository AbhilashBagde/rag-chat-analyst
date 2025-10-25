import os
import sys
from io import BytesIO
from typing import List, Dict, Any

# Required third-party libraries:
# pip install langchain-community pypdf chromadb
# Be sure Ollama is running (ollama serve) and the models listed below are pulled:
# ollama pull llama3.2:3b
# ollama pull mxbai-embed-large:latest

try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.embeddings import OllamaEmbeddings
    from langchain_community.llms import Ollama
    from langchain_community.vectorstores import Chroma
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.chains import create_retrieval_chain
    from langchain_core.documents import Document
except ImportError:
    print("Error: Required Python libraries not found.")
    print("Please install them using: pip install langchain-community pypdf chromadb")
    sys.exit(1)

# --- CONFIGURATION ---
# NOTE: Ensure your Ollama server is running (run 'ollama serve' in a terminal)
OLLAMA_BASE_URL = "http://localhost:11434"
# Using the user's available models
LLM_MODEL = "llama3.2:3b"  
EMBEDDING_MODEL = "mxbai-embed-large:latest" 
PDF_PATH = "csr_chat_transcript.pdf"
VECTOR_DB_PATH = "./chat_rag_db"

# --- 1. MOCK PDF CONTENT FOR DEMONSTRATION ---
# Since I cannot access your local file system, we will use a Document list 
# containing mock chat data. REPLACE THIS WITH THE ACTUAL PDF LOADING BELOW.
MOCK_CHAT_CONTENT = [
    "--- CSR Chat Transcript - Order 78901 ---\n",
    "Client: My order 78901 was supposed to arrive today, but the tracking shows 'Delayed'. What is the new estimated delivery date (EDD)?",
    "CSR: I apologize for the delay. Order 78901 for the Nebula 5000 is currently stuck in transit at the Chicago hub due to weather. The revised EDD is now Saturday, 3 days from now.",
    "Client: Is there any way to expedite it? I need it for a presentation on Friday.",
    "CSR: Unfortunately, standard shipping cannot be expedited once in this stage. However, I can offer you a 15% discount on your next accessory purchase as compensation for the inconvenience.",
    "Client: What about the warranty? Does this delay affect the 1-year guarantee I purchased?",
    "CSR: Not at all. The 1-year guarantee starts upon successful delivery, which will be Saturday. I have documented the delay under ticket #RAG-2025.",
    "Client: That 15% offer sounds fair. Please apply it to my account. Thank you.",
    "CSR: You are welcome. The 15% coupon is now active on your account under the name 'COMP-78901'. Have a great day."
]

def load_documents(path: str) -> List[Document]:
    """Loads a PDF document or uses mock content if the file is not found."""
    print(f"Attempting to load documents from: {path}")
    if os.path.exists(path):
        try:
            # Load from the real PDF file
            loader = PyPDFLoader(path)
            documents = loader.load()
            print(f"Successfully loaded {len(documents)} pages from '{path}'.")
            return documents
        except Exception as e:
            print(f"Error loading PDF: {e}")
            print("Falling back to mock content for demonstration.")
            # Fallback to mock content
            return [Document(page_content="\n".join(MOCK_CHAT_CONTENT), metadata={"source": "mock_chat_transcript"})]
    else:
        print(f"PDF file not found at '{path}'.")
        print("Using mock chat content instead. Please create or update the PDF_PATH to use your actual file.")
        # Use mock content if file is missing
        return [Document(page_content="\n".join(MOCK_CHAT_CONTENT), metadata={"source": "mock_chat_transcript"})]

def setup_rag_system():
    """Sets up the RAG system: loads data, creates chunks, and initializes the Vector Store and Chain."""
    
    # 1. Load Documents
    docs = load_documents(PDF_PATH)
    
    # 2. Split Documents into Chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Split document into {len(chunks)} chunks.")

    # 3. Initialize Ollama Components (LLM and Embeddings)
    llm = Ollama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL)
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL)

    # 4. Create or Load Vector Store (ChromaDB)
    # This stores the chunks and their embeddings locally.
    print(f"Creating/Loading vector store at: {VECTOR_DB_PATH}")
    vector_store = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=VECTOR_DB_PATH
    )
    retriever = vector_store.as_retriever()
    
    # 5. Define the Agentic/Expert System Prompt
    system_prompt = (
        "You are an expert Chat Transcript Analyst for a Customer Service organization. "
        "Your task is to answer user questions based STRICTLY on the provided chat excerpts. "
        "The context is a conversation between a Client and a CSR. "
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
    
    # 6. Create the Document and Retrieval Chains
    document_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)
    
    return retrieval_chain

def run_chatbot(rag_chain: Any):
    """Runs the interactive Q&A loop."""
    print("\n--- Agentic Chat Transcript Q&A Chatbot ---")
    print(f"LLM: {LLM_MODEL} | Embeddings: {EMBEDDING_MODEL}")
    print("Ask questions about the chat transcript. Type 'exit' or 'quit' to end.")

    while True:
        try:
            user_input = input("\nQuery > ")
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting Chatbot. Goodbye!")
                break
            
            if not user_input.strip():
                continue

            print("Thinking... (Retrieving context and generating response)")
            
            # Invoke the RAG chain
            response = rag_chain.invoke({"input": user_input})
            
            # Display the result
            print("\n--- Analyst Response ---")
            print(response["answer"])
            
            # Optional: Display the retrieved documents
            print("\n--- Retrieved Contexts ---")
            for doc in response["context"]:
                print(f"Source: {doc.metadata.get('source', 'Unknown')} | Snippet: {doc.page_content[:150]}...")
            
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            print("Please ensure Ollama is running and both models are pulled.")
            break

if __name__ == "__main__":
    try:
        # 1. Setup the RAG system (Loading, Chunking, Embedding, Chain Creation)
        rag_chain = setup_rag_system()
        
        # 2. Run the interactive interface
        run_chatbot(rag_chain)

    except Exception as e:
        print(f"A critical error occurred during initialization: {e}")
        print("Make sure you have all dependencies installed and Ollama is running.")