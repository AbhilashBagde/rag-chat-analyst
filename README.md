Amazing. You’re about to ship this like a product 👍

What you’re asking for is basically a “Full Setup & User Guide” that lives in your repo so someone non-technical (your sister, a manager, etc.) can follow it step by step and get the chatbot running on their own laptop.

I’ll write this as a full `README.md` replacement. It will assume macOS (which matches you), but I’ll also sprinkle Windows notes where it matters.

You can copy-paste this straight into `README.md` in your repo.

---

# RAG Transcript Analyst

Local AI Chatbot for Customer Support Conversations
**No API keys. No cloud. 100% local.**

---

## 💡 What this project does

This project lets you:

* Upload (replace) a customer support transcript PDF.
* Ask natural questions like “Did we offer a refund?” or “What went wrong for this customer?”
* Get grounded answers based ONLY on that PDF.
* See sources for each answer.
* Run everything locally on your own machine.

It’s basically a private “ChatGPT for transcripts” that never sends data to any external server.

---

## 🧠 How it works (high level)

1. Your PDF is split into chunks.
2. Each chunk is embedded and stored in a local vector DB (ChromaDB).
3. When you ask a question:

   * The system finds the most relevant chunks from your PDF.
   * Those chunks are passed to a local LLM running in Ollama.
   * The LLM answers using only that context.

Stack:

* **Ollama** for the LLM and embeddings (runs locally).
* **ChromaDB** for retrieval.
* **FastAPI** for the backend API.
* **A simple web UI** that looks like a chat app.

---

## 🖥️ What you’ll end up with

After setup, you’ll have:

* A web chat UI at `http://127.0.0.1:8000`
* A text box where you can ask questions
* Answers that reference your PDF

You can hand this repo to someone else, and all they have to do is follow this guide.

---

## 1. Prerequisites (Install these once)

### 1.1 Install Python 3 (3.10+ recommended)

Mac usually has `python3` already. You can check by running in Terminal:

```bash
python3 --version
```

If it's 3.10 or higher, you're good.
If it's older than 3.10, install a newer Python from python.org.

> Windows: install Python from python.org and make sure “Add Python to PATH” is checked during install.

---

### 1.2 Install Git

You can check if you have Git:

```bash
git --version
```

If not installed, on macOS:

* Install Xcode Command Line Tools by running:

  ```bash
  xcode-select --install
  ```

Windows:

* Install Git for Windows from git-scm.com.

---

### 1.3 Install Ollama

Ollama is the engine that runs the local AI models on your machine.

1. Go to `https://ollama.com` and download/install Ollama for your OS.
2. After installing, open Terminal and run:

   ```bash
   ollama --version
   ```

If that prints a version, you’re good.

---

### 1.4 Pull the required AI models

We’ll use:

* `llama3.2:3b` as the reasoning model for answers
* `mxbai-embed-large:latest` as the embedding model for search/retrieval

In Terminal, run:

```bash
ollama pull llama3.2:3b
ollama pull mxbai-embed-large:latest
```

These download once and stay on your machine.

---

## 2. Get the project code

### Option A: You already have the folder

If you already cloned/downloaded this repo, skip to step 3.

### Option B: You’re setting up on a new machine

In Terminal:

```bash
git clone https://github.com/AbhilashBagde/rag-chat-analyst.git
cd rag-chat-analyst
```

Now you should be inside the project folder.

Run:

```bash
ls
```

You should see files like:

* `server.py`
* `requirements.txt`
* `csr_chat_transcript.pdf`
* `.gitignore`
* `README.md`

---

## 3. Create and activate a virtual environment

We use a virtual environment so we don’t mess up your main Python install.

Run these commands from inside the `rag-chat-analyst` folder:

### macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

After activation, your terminal prompt will change and start with `(.venv)`.

> If you ever close the terminal and come back later, just `cd` into the project and run:
>
> ```bash
> source .venv/bin/activate
> ```
>
> (or on Windows: `.\.venv\Scripts\Activate.ps1`)

---

## 4. Install Python dependencies

Run this (still inside the `rag-chat-analyst` folder, and with the virtual environment active):

```bash
pip install -r requirements.txt
```

This installs:

* FastAPI (the web server)
* Uvicorn (runs the server)
* LangChain (RAG pipeline glue)
* ChromaDB (local vector DB)
* pypdf (reads your transcript PDF)
* ollama (talks to your local LLM)

---

## 5. Put in your transcript

This app is designed to analyze one transcript PDF at a time.

Default filename used by the app is:

```text
csr_chat_transcript.pdf
```

So you have two choices:

### Option 1 (recommended)

Replace the existing `csr_chat_transcript.pdf` in the folder with your own PDF, but keep the same filename.

### Option 2 (custom filename)

If you don’t want to rename your PDF:

1. Open `server.py`
2. Find this line:

   ```python
   PDF_PATH = "csr_chat_transcript.pdf"
   ```
3. Change it to match your file, e.g.:

   ```python
   PDF_PATH = "my_customer_chat.pdf"
   ```

Save the file.

---

## 6. Start Ollama

Ollama must be running so we can ask the model questions.

In a NEW terminal window/tab (leave your first one alone), run:

```bash
ollama serve
```

Leave that running. That is your local AI brain.

If you see nothing or an error, try just running `ollama` (on mac, Ollama.app may already be managing the server for you).

---

## 7. Start the chatbot server

Go back to the FIRST terminal tab (the one where you activated `.venv`, installed requirements, etc.) and run:

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

You should now see logs like:

```text
[SERVER] Initializing RAG System...
[SERVER] ✅ RAG System Ready. Models: llama3.2:3b & mxbai-embed-large:latest.
[SERVER] ✅ Data loaded from: csr_chat_transcript.pdf
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Important things happening here:

* Your PDF is being read.
* It’s being chunked and embedded.
* A local vector DB is built in the `chat_rag_db/` folder (which is ignored by git).
* The FastAPI server is now live at `http://127.0.0.1:8000`.

If you instead see something like:

* “Could not connect to Ollama” → You didn’t start `ollama serve`.
* “File not found” → The PDF filename in `server.py` doesn’t match what’s in the folder.

---

## 8. Use the chatbot in the browser

### Option A (recommended, final version)

Just open this in your browser:

```text
http://127.0.0.1:8000
```

You’ll see a dark chat-style interface that looks like this:

* You (right aligned, blue bubble)
* Analyst Bot (left aligned, gray bubble)
* Input box at the bottom

You can now:

* Ask: `summarize the main issue in this chat`
* Ask: `did the agent offer any refund or compensation?`
* Ask: `what is the promised delivery date?`
* Ask: `what does the customer want fixed?`

And it will answer using ONLY the transcript.

### Option B (debug / testing)

You can also open:

```text
http://127.0.0.1:8000/docs
```

That shows a testing UI (Swagger docs). You can click the `/query` endpoint, hit "Try it out", send a question, and see the raw JSON response.

---

## 9. Stopping the app

To stop the server:

* Go to the terminal running `uvicorn ...` and press `Ctrl + C`.

To stop Ollama:

* Go to the terminal running `ollama serve` and press `Ctrl + C`.

To exit the virtual environment:

```bash
deactivate
```

You can always reactivate later with `source .venv/bin/activate`.

---

## 10. Changing to a new transcript later

Want to analyze a different conversation?

1. Stop the server (`Ctrl + C`).
2. Replace `csr_chat_transcript.pdf` with the new chat PDF (same name).

   * OR update `PDF_PATH` in `server.py` if you want a different name.
3. Delete the old vector DB folder if you want to force a clean re-index:

   ```bash
   rm -rf chat_rag_db
   ```
4. Restart Ollama (if needed) and restart the server:

   ```bash
   uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```
5. Open `http://127.0.0.1:8000` and ask questions again.

Now the answers are based on the new PDF.

---

## 11. Folder / file reference

Here’s what each important file does:

* `server.py`
  The backend.

  * Starts FastAPI.
  * Loads and chunks the PDF.
  * Builds a ChromaDB vector store.
  * Connects to Ollama (LLM + embeddings).
  * Serves:

    * `GET /` → chat UI HTML
    * `POST /query` → answer questions
    * `GET /docs` → debug API docs

* `requirements.txt`
  Python libraries needed for this to run.

* `csr_chat_transcript.pdf`
  The transcript being analyzed. You can swap this with your own.

* `chat_rag_db/`
  Auto-generated local vector DB of your PDF chunks. This is what makes retrieval fast.
  (Ignored by git so your data stays on your machine only.)

* `.venv/`
  Your private Python environment for this project.
  (Also ignored by git.)

* `.gitignore`
  Makes sure you don’t accidentally upload `.venv`, your local DB, cache files, etc.

---

## 12. FAQ / Troubleshooting

### ❓ I opened `http://127.0.0.1:8000` and saw `{"detail": "Not Found"}`

This means your `server.py` might be an older version that doesn’t include the UI route.

Your `server.py` should have something like:

```python
from fastapi.responses import HTMLResponse

CHAT_HTML = """... a big HTML string ..."""

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    return CHAT_HTML
```

If that’s not there, add it (you can copy from the version in this repo), restart `uvicorn`, and refresh the browser.

---

### ❓ It says “I couldn’t reach Ollama”

That means the backend tried to call the local AI model but couldn’t.

Fix:

1. In a new terminal:

   ```bash
   ollama serve
   ```
2. Make sure you have both required models pulled:

   ```bash
   ollama pull llama3.2:3b
   ollama pull mxbai-embed-large:latest
   ```
3. Restart the FastAPI server.

---

### ❓ I changed the PDF, but I’m still getting answers about the old chat

That means ChromaDB is still using the previous embeddings.

Fix:

1. Stop the server (`Ctrl + C` where uvicorn is running).
2. Delete the DB folder:

   ```bash
   rm -rf chat_rag_db
   ```
3. Start the server again with:

   ```bash
   uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```

Now it will rebuild from the new PDF.

---

### ❓ Can I give this to someone else?

Yes. They just need:

1. Python
2. Git
3. Ollama
4. This repo

Then they follow exactly the same steps:

* create venv
* pip install
* `ollama pull ...`
* `ollama serve`
* `uvicorn ...`
* open browser

Their data stays local to them.

---

## 13. TL;DR Quickstart (copy/paste cheat sheet)

```bash
# 0. Clone repo
git clone https://github.com/AbhilashBagde/rag-chat-analyst.git
cd rag-chat-analyst

# 1. Create and activate virtual env
python3 -m venv .venv
source .venv/bin/activate            # Windows: .\.venv\Scripts\Activate.ps1

# 2. Install deps
pip install -r requirements.txt

# 3. Pull and run the local models (in a second terminal tab)
ollama pull llama3.2:3b
ollama pull mxbai-embed-large:latest
ollama serve

# 4. Start the chatbot server (back in first tab)
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# 5. Open your browser
http://127.0.0.1:8000

# 6. Ask questions about csr_chat_transcript.pdf
```

---

You’re done.
You don’t just have code anymore — you have a product with onboarding.
