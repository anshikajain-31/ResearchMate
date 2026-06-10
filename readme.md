# ResearchMate 🔍

An AI-powered conversational assistant that lets students and researchers chat with academic papers — ask questions, verify claims, and search for recent developments, all in one seamless interface.

Uploading and reading dense research papers is time-consuming. ResearchMate goes beyond standard RAG systems by combining intelligent document ingestion, session-aware vector search, a LangGraph-based reasoning agent, and a lightweight side-channel for real-time, off-topic questions.

---

## 🚀 Key Features

| Feature | Description |
| --- | --- |
| **Multi-Source Ingestion** | Load papers via local file upload (`.pdf`, `.txt`, `.md`), web URLs, or directly via ArXiv IDs (e.g., `2303.08774`). |
| **Context-Grounded Q&A** | Ask questions directly about your uploaded literature. The system retrieves relevant sections and generates grounded answers. |
| **Claim Verification** | Ask *"Is this claim still valid?"* The system cross-references with recent literature and live web contexts to find confirming or contradictory evidence. |
| **Real-Time Web Search** | Integrates Tavily API to automatically pull live web data and recent developments for time-sensitive questions. |
| **`/btw` Side-Channel** | Ask off-topic or general knowledge questions (e.g., `/btw What is the difference between RLHF and DPO?`) without polluting your research session history. |
| **Multi-Session Isolation** | Run multiple independent research sessions simultaneously. Each session gets its own isolated Qdrant vector collection and auto-generated title based on your first message. |
| **Token Streaming** | Responses stream token-by-token in the UI for a highly responsive user experience. |

---

## 🏗️ Architecture & Workflow

The system is split into a streamlined frontend layer, a document-processing layer, a session-scoped vector database, and an orchestrated LangGraph agent workflow.

### Project Structure

```text
ResearchMate/
├── app.py                     # Main Streamlit UI and session management
├── main.py                    # Lightweight Gemini smoke-test entry point
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Project metadata
├── .env.example               # Example environment variables
├── qdrant_login_steps.md      # Qdrant Cloud setup guide
├── backend/
│   ├── btw_handler.py         # Off-topic / live-info side-channel handler
│   ├── models.py              # Pydantic models for structured routing decisions
│   ├── paper_loader.py        # Document loaders (PDF, text, MD, URL, ArXiv)
│   ├── rag_graph.py           # LangGraph reasoning state machine
│   └── vector_store.py        # Qdrant vector store configuration + Gemini embeddings
└── embedding_cache/           # Local cache to prevent redundant embedding API calls
```

### LangGraph Routing Flow

When a query is submitted, the LangGraph state machine determines the execution path:

```text
          User Query
              │
              ▼
      Router (Gemini LLM)
              │
              ├──► direct_answer ─────────────────────────► Generate Answer
              │
              ├──► retrieve ──► Retriever + Web Tools ──► Relevancy Check
              │                      │                        │
              │                      │◄── Query Rewrite ───────┘ (max 1 retry)
              │                      └───────────────────────────► Generate Answer
              │
              └──► verify_claim ──► Web Search + ArXiv Search ──► Verdict + Links
```

---

## 🧠 Design Decisions

| Decision | Technical Reasoning |
| --- | --- |
| **Max 3 Retrieval Attempts** | Prevents infinite tool-call loops; the agent falls back to plain LLM generation after 3 attempts, keeping the message history clean for the checkpointer. |
| **Max 1 Query Rewrite** | After one rewrite pass, the graph falls through to `generate_answer` rather than cycling indefinitely on vague queries. |
| **Chunk Size 1000 / Overlap 200** | Balances granular retrieval precision with semantic continuity across chunk boundaries. |
| **Session-Scoped Collections** | Dynamically creates isolated Qdrant collections (`ResearchMate_{session_id}`) to guarantee total data privacy between concurrent users. |
| **Dual-Track Claim Verification** | Combines broad web searches (blogs/news/industry) with dedicated `site:arxiv.org` searches to capture peer-reviewed counter-arguments. |
| **k = 4 Retrieval Chunks** | Provides optimal context density for grounded answers without overloading the prompt token budget. |
| **Embedding Cache** | `CacheBackedEmbeddings` (blake2b keys) ensures identical text blocks are never re-embedded, saving API costs and latency. |
| **Gemini Embedding Model** | Uses `models/gemini-embedding-2` at 3072 dimensions for high-fidelity semantic search. |

---

## 🛠️ Setup & Installation

### Prerequisites

- Python 3.10 or newer
- [`uv`](https://docs.astral.sh/uv/) package manager
- Google AI Studio account (Gemini API key)
- Qdrant Cloud cluster (or a local instance via Docker)
- Tavily Search API account

### 1. Clone and Install

```bash
# Clone the repository
git clone <repo-url>
cd ResearchMate

# Install all dependencies
uv sync
```

### 2. Configure Environment Variables

```bash
# Copy the example env file and fill in your keys
cp .env.example .env
```

Edit `.env` with your credentials:

```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
QDRANT_URL=https://your-qdrant-cluster-url
QDRANT_API_KEY=your_qdrant_api_key
```

| Variable | Purpose | Where to get it |
| --- | --- | --- |
| `GEMINI_API_KEY` | LLM inference, routing, and embeddings | [Google AI Studio](https://aistudio.google.com/) |
| `TAVILY_API_KEY` | Live web search and claim verification | [Tavily Dashboard](https://tavily.com/) |
| `QDRANT_URL` | Endpoint for the remote vector store | [Qdrant Cloud](https://cloud.qdrant.io/) |
| `QDRANT_API_KEY` | Authentication token for your cluster | [Qdrant Cloud](https://cloud.qdrant.io/) |

### 3. Run the App

```bash
uv run streamlit run app.py
```

To run a backend module directly (useful during development):

```bash
uv run python -m backend.<module_name>
```

---

## 📖 Recommended Workflow

1. **Launch the interface** with `uv run streamlit run app.py`.
2. **Load your material** — expand the sidebar to upload a PDF/text file, paste a URL, or enter an ArXiv ID.
3. **Ask questions** about the paper content:
   > *"Summarize the key architectural breakthroughs introduced in this paper."*
4. **Verify claims** from the text:
   > *"Verify the claim that transformers outperform state-of-the-art RNNs on all long-context NLP tasks."*
5. **Use `/btw`** for quick off-topic questions that shouldn't pollute your session:
   > */btw What is the difference between RLHF and DPO?*
6. **Monitor the graph** — use the graph-state panel in the UI to watch backend routing, query rewrites, and verification verdicts in real time.

---



