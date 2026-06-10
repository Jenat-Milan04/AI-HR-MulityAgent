# HR Multi-Agent Task Routing & Memory Engine

> ZeloraTech AI Intern Technical Challenge — Full Backend Submission

A production-ready multi-agent HR automation system built with **FastAPI** + **LangGraph**, featuring intent classification, agent routing, two-tier memory, and append-only audit logging.

---

## Architecture

```
User Request (POST /request)
        │
        ▼
┌─────────────────────────────────────────┐
│         LangGraph Orchestrator          │
│                                         │
│  1. memory_lookup   — STM + LTM fetch   │
│  2. classify_intent — keyword scoring   │
│  3. route_agent     — dispatch + retry  │
│  4. save_memory     — STM + LTM write   │
│  5. save_audit      — append-only log   │
└─────────────────────────────────────────┘
        │
        ▼
┌────────────┬───────────┬─────────────┬──────────────┐
│ Scheduling │   Leave   │ Compliance  │Clarification │
│   Agent    │   Agent   │   Agent     │   Agent      │
└────────────┴───────────┴─────────────┴──────────────┘
        │
        ▼
┌─────────────────────────────────────────┐
│            LLM Provider Layer           │
│                                         │
│   MockProvider  │  OpenAIProvider       │
│                 │  OllamaProvider       │
└─────────────────────────────────────────┘
        │
        ▼
SQLite Database (memory + audit_logs)
```

---

## LLM Provider System

The system supports **three interchangeable backends** selected via `MODEL_PROVIDER` in `.env`.
No agent code changes are needed to switch providers.

### Mock Mode (default)

```
MODEL_PROVIDER=mock
```

- Zero cost — no API key required
- Fully deterministic — ideal for CI, automated tests, and local demos
- Keyword-based responses that cover all HR domains

### OpenAI Mode

```
MODEL_PROVIDER=openai
OPENAI_API_KEY=sk-...
MODEL_NAME=gpt-4o-mini
```

- Real AI-generated responses via OpenAI Chat Completions
- Requires a valid `OPENAI_API_KEY`

### Ollama Mode (local open-source LLM)

```
MODEL_PROVIDER=ollama
MODEL_NAME=llama3
OLLAMA_BASE_URL=http://localhost:11434
```

- Uses any model you have pulled locally via [Ollama](https://ollama.com)
- No API key, no external calls — fully air-gapped

### Provider Architecture

```
User
  │
  ▼
Orchestrator
  │
  ▼
Agent (Leave / Scheduling / Compliance / Clarification)
  │
  └──▶ get_llm_provider()
            │
            ├──▶ MockLLMProvider
            ├──▶ OpenAIProvider
            └──▶ OllamaProvider
```

Agents call `provider.generate(message, context)` — they are fully decoupled
from the backend. Switching providers requires only a one-line `.env` change.

---

## Quick Start

### 1. Clone & Install

```bash
cd hr_agent
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Default: mock mode (no API key needed)
cp .env .env.local
# To use OpenAI: set MODEL_PROVIDER=openai and add OPENAI_API_KEY
```

### 3. Start the Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Interactive API Docs

Open: http://localhost:8000/docs

---

## API Endpoints

| Method | Endpoint              | Description                      |
|--------|-----------------------|----------------------------------|
| POST   | `/request`            | Submit an HR request             |
| GET    | `/audit`              | Retrieve audit logs              |
| GET    | `/memory/{user_id}`   | Get user's STM + LTM             |
| POST   | `/memory`             | Manually add a memory entry      |
| GET    | `/health`             | Health check                     |

### Example: Submit a Leave Request

```bash
curl -X POST http://localhost:8000/request \
  -H "Content-Type: application/json" \
  -d '{"user_id": "emp_001", "message": "I need leave next Friday"}'
```

Response:
```json
{
  "user_id": "emp_001",
  "response": "Leave request acknowledged. Please confirm the leave type...",
  "intent": "LEAVE",
  "confidence": 0.55,
  "agent": "LeaveAgent",
  "status": "success"
}
```

### Example: Check Audit Logs

```bash
curl "http://localhost:8000/audit?user_id=emp_001&limit=5"
```

### Example: Retrieve Memory

```bash
curl http://localhost:8000/memory/emp_001
```

---

## Project Structure

```
hr_agent/
├── app/
│   ├── llm/
│   │   ├── __init__.py        ← get_llm_provider() factory
│   │   ├── base.py            ← BaseLLMProvider interface
│   │   ├── mock_provider.py   ← Deterministic mock (default)
│   │   ├── openai_provider.py ← OpenAI Chat Completions
│   │   └── ollama_provider.py ← Local Ollama instance
│   ├── api/
│   │   ├── models.py          ← Pydantic request/response models
│   │   └── routes.py          ← All 5 FastAPI endpoints
│   ├── agents/
│   │   ├── scheduler.py       ← Scheduling Agent
│   │   ├── leave.py           ← Leave Agent
│   │   ├── compliance.py      ← Compliance Agent
│   │   └── clarification.py   ← Fallback Clarification Agent
│   ├── memory/
│   │   ├── stm.py             ← Short-Term Memory (ring buffer, 10 entries)
│   │   └── ltm.py             ← Long-Term Memory (significance-gated)
│   ├── services/
│   │   ├── classifier.py      ← Intent classification engine
│   │   ├── router.py          ← Agent dispatcher
│   │   ├── audit.py           ← Append-only audit logger
│   │   └── orchestrator.py    ← LangGraph state machine
│   ├── db/
│   │   └── database.py        ← SQLite init + connection helper
│   └── main.py                ← FastAPI app entry point
├── tests/
│   └── test_system.py         ← Full test suite (pytest)
├── frontend/
│   └── index.html             ← Optional chat UI
├── .env
├── requirements.txt
└── README.md
```

---

## Running Tests

```bash
pytest tests/ -v
```

All tests use an in-memory SQLite database so they are isolated and fast.
Mock mode is always used in tests — no API credits consumed.

---

## Memory System

### Short-Term Memory (STM)
- Stores the **10 most recent** conversation turns per user
- Oldest entries are automatically pruned
- All messages are saved to STM regardless of significance

### Long-Term Memory (LTM)
- Only stores messages with **significance score ≥ 0.7**
- Significance is computed by keyword matching (leave, manager, policy, schedule, etc.)
- Base score: 0.2 — each matched keyword adds 0.1, capped at 1.0

| Message | Score |
|---------|-------|
| "hello" | 0.2 |
| "I need leave" | 0.3 |
| "I need leave and my manager is Sarah" | 0.5 |
| "Annual leave request, manager Sarah, policy question" | 0.7+ → stored in LTM |

---

## Intent Classification

| Intent | Trigger Keywords |
|--------|-----------------|
| SCHEDULING | schedule, meeting, interview, calendar, book, reschedule, slot |
| LEAVE | leave, vacation, day off, sick, absence, holiday, annual leave |
| COMPLIANCE | policy, rule, compliance, remote work, wfh, guideline |
| CLARIFICATION | Fallback when confidence < 0.5 |

Confidence score formula:
- Base: 0.4
- +0.15 per matched keyword
- Capped at 0.98

---

## Retry & Timeout Logic

Every agent uses:
- **3 retries** (configurable via `MAX_RETRIES` in `.env`)
- **10-second timeout** per attempt (configurable via `REQUEST_TIMEOUT`)
- Graceful degradation: users see a friendly error message, never a raw traceback

---

## Audit Log

- Append-only: **INSERT only**, never UPDATE or DELETE
- Required fields: `id`, `timestamp`, `user_id`, `request`, `intent`, `agent`, `response`, `status`

---

## Frontend

Open `frontend/index.html` in a browser while the backend is running.  
No build step required — pure HTML/CSS/JS.
