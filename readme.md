# ResearchMate 🔍

An AI-powered conversational assistant that lets students and researchers chat with academic papers—ask questions, verify claims, and search for recent developments, all in one seamless interface.

Uploading and reading dense research papers is time-consuming. ResearchMate goes beyond standard RAG systems by combining intelligent document ingestion, session-aware vector search, a LangGraph-based reasoning agent, and a lightweight side-channel for real-time, off-topic questions.

---

## 🚀 Key Features

| Feature | Description |
| --- | --- |
| **Multi-Source Ingestion** | Load papers via local file upload (`.pdf`, `.txt`, `.md`), web URLs, or directly via ArXiv IDs (e.g., `2303.08774`). |
| **Context-Grounded Q&A** | Ask questions directly about your uploaded literature. The system retrieves relevant sections and generates grounded answers. |
| **Claim Verification** | Ask *"Is this claim still valid?"* The system cross-references the text with recent literature and live web contexts to find confirming or contradictory evidence. |
| **Real-Time Web Search** | Integrates Tavily API to automatically pull down live web data and recent developments for time-sensitive questions. |
| **`/btw` Side-Channel** | Ask off-topic or general knowledge questions (e.g., `/btw What is the difference between RLHF and DPO?`) without polluting your research session history. |
| **Multi-Session Isolation** | Run multiple independent research sessions simultaneously. Each session gets its own isolated Qdrant vector collection and auto-generated titles based on your first message. |
| **Token Streaming** | Responses stream token-by-token in the UI, ensuring a highly responsive user experience. |

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
              │                      │◄── Query Rewrite ───────┘ (Max 3 retries)
              │                      └───────────────────────────► Generate Answer
              │
              └──► verify_claim ──► Web Search + ArXiv Search ──► Verdict + Links

```

---

## 🧠 Design Decisions

| Decision | Technical Reasoning |
| --- | --- |
| **Max 3 Query Rewrites** | Prevents infinite loops on highly ambiguous or vague queries; gracefully falls back to a direct LLM answer after 3 attempts. |
| **Chunk Size 1000 / Overlap 200** | Balances granular retrieval precision with semantic continuity across chunk boundaries. |
| **Session-Scoped Collections** | Dynamically creates isolated Qdrant collections (`session_{uuid}`) to guarantee total data privacy between concurrent user threads. |
| **Dual-Track Claim Verification** | Combines broad web searches (for blogs/news/industry updates) with dedicated `site:arxiv.org` searches to capture peer-reviewed counter-arguments. |
| **$k=4$ Retrieval Chunks** | Provides optimal context density for rich, fully-grounded answers without overloading the prompt token limit. |
| **Embedding Cache** | Ensures identical text text-blocks are never re-embedded twice, significantly saving API costs and improving performance. |

---

## 🛠️ Setup & Installation

### Prerequisites

* Python 3.10 or newer
* Google AI Studio Account (Gemini API key)
* Qdrant Cloud Cluster (or a local instance running via Docker)
* Tavily Search API Account

### 1. Clone and Environment Setup

```bash
git clone <your-repo-url>
cd ResearchMate

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

```

### 2. Configuration

Create a `.env` file in the root directory of the project:

```env
GEMINI_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
QDRANT_URL=https://your-qdrant-cluster-url
QDRANT_API_KEY=your_qdrant_api_key

```

| Variable | Purpose | Location |
| --- | --- | --- |
| `GEMINI_API_KEY` | Controls LLM inference, routing, and embeddings. | [Google AI Studio](https://aistudio.google.com/) |
| `TAVILY_API_KEY` | Drives live web searches and claim verification. | [Tavily Dashboard](https://tavily.com/) |
| `QDRANT_URL` | Endpoint for the remote semantic vector store. | [Qdrant Cloud](https://cloud.qdrant.io/) |
| `QDRANT_API_KEY` | Secure authentication token for your cluster. | [Qdrant Cloud](https://cloud.qdrant.io/) |

---

## 📖 Recommended Workflow

1. **Launch the Interface:**
```bash
streamlit run app.py

```


2. **Load Your Material:** Expand the sidebar panel to upload papers or provide an ArXiv ID.
3. **Analyze & Extract:** Ask questions like:
> *"Summarize the key architectural breakthroughs introduced in this paper."*


4. **Stress-Test Claims:** Validate statements inside the text by asking:
> *"Verify the claim that transformers outperform state-of-the-art RNNs on all long-context NLP tasks."*


5. **Inspect the Graph:** Use the graph-state panel in the UI to monitor the backend agent routing, query rewrites, and verification verdicts in real time.

---

## 🔧 Troubleshooting

* **Missing / Outdated Context:** If document searches return empty or weak responses, navigate to the sidebar to verify the document was successfully parsed, or try adjusting your question terms to trigger the automated query re-writer.
* **Qdrant Connection Timeout:** Double-check your cluster's structural URI endpoint in your `.env`. Ensure your network allows outbound requests to your hosted Qdrant cluster on port `6333` or `6334`.
* **API Key Limits:** If streaming fails mid-sentence, ensure your Gemini or Tavily usage tiers haven't hit standard rate limits.

---

## 🔮 Future Roadmap

* 🔐 **Authentication Workspaces:** Add secure user sign-ins and persistent historical project boards.
* 🔗 **Citation Auto-Linking:** Inject deep anchor links matching inline text directly to source PDF page/paragraph numbers.
* 📊 **Multi-Paper Benchmarking:** Introduce comparative analysis modes allowing the matrix cross-examination of multiple documents side by side.
* 📂 **Export Engine:** One-click downloads for synthesized lit-reviews, evidence summaries, and markdown-formatted notes.