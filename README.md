Agentic RAG Chat Transcript Analyst

This project is a simple Retrieval-Augmented Generation (RAG) chatbot designed to analyze customer service chat transcripts. It uses LangChain for orchestration, ChromaDB for vector storage, and Ollama for running open-source Language Models (LLMs) and embeddings locally.

🚀 Quick Start Guide (5 Steps)

Follow these steps to get the chat analyst running on your local machine.

Step 1: Clone the Repository

Open your terminal (Terminal on Mac/Linux, Command Prompt/PowerShell on Windows) and run this command to download the project files:

git clone [(https://github.com/AbhilashBagde/rag-chat-analyst)]
cd rag-chat-analyst


(Note: Replace the URL with the actual link to your GitHub repository.)

Step 2: Set Up Ollama and Models (Local AI)

Ollama manages the large language models (LLMs) that power the chatbot. This step only needs to be done once.

Install Ollama:
Download and install the application for your operating system from the official website:
Ollama Download Page

Start Ollama:
Make sure the Ollama application is running in the background.

Download Models:
In your terminal, pull the required LLM and Embedding models. This may take a few minutes as it downloads the model files:

ollama pull llama3.2:3b
ollama pull mxbai-embed-large:latest


Step 3: Install Python Dependencies

This project uses a virtual environment for a clean setup.

Create a Virtual Environment:

python3 -m venv .venv


Activate the Environment:

source .venv/bin/activate


(You should see (.venv) appear in your terminal, confirming it's active.)

Install Libraries:
Install all required Python packages listed in requirements.txt:

pip install -r requirements.txt


Step 4: Prepare Your Data (The PDF)

The chatbot is designed to read a single PDF file named csr_chat_transcript.pdf.

Replace the File: Delete the placeholder file named csr_chat_transcript.pdf (if it exists).

Add Your File: Take your new chat transcript file (it must be a valid PDF document, not just a text file renamed) and place it in the main project folder.

Rename: Rename your new PDF file to exactly: csr_chat_transcript.pdf

Step 5: Run the Chatbot

With your dependencies installed and Ollama running, you can now start the bot!

Run the main script:

python rag_chatbot.py


Chat! You will see the Query > prompt. Ask questions about the content of your PDF file, like "What was the final resolution for Priya Mehra's billing issue?"

Exit: To quit the chatbot, type exit or quit and press Enter.

🧹 Cleaning Up

If you ever need to stop working on the project, you can easily exit the virtual environment:

deactivate


This returns you to your normal system shell.