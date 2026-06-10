# Design Report: HR Multi-Agent Task Routing & Memory Engine

**Candidate Submission — ZeloraTech AI Intern Challenge**  
**Date:** 2026-06-09

---

## 1. Overview

This report explains the key design decisions, trade-offs, and known limitations of the submitted system.

---

## 2. Design Decisions

### 2.1 LangGraph as the Orchestration Layer

LangGraph was chosen because it provides:
- **Typed state** shared across all nodes, eliminating implicit global state bugs
- **Explicit edge definitions** that make the routing pipeline easy to audit and extend
- **Async support** (`ainvoke`) which integrates cleanly with FastAPI's async model
- **Future extensibility**: adding a new node (e.g. a "notification" node after the agent responds) requires adding one `add_node` + `add_edge` call

The pipeline is linear for this submission (memory → classify → route → save_memory → save_audit → END). In a production system, this could branch conditionally (e.g. skip LTM save if status = error).

### 2.2 Keyword-Based Intent Classification

The classifier uses keyword matching rather than an LLM call for intent classification.

**Reasons:**
- **Deterministic**: same input always produces the same output — easier to test and debug
- **No API key required**: the system runs without an OpenAI key
- **Fast**: no network round-trip for classification
- **Transparent**: the `matched_keywords` field in the result shows exactly why an intent was chosen

**Trade-off:** Keyword matching will fail on ambiguous phrasing like "I'm out next week" (could be leave or scheduling). In production, this should be replaced with an LLM-based classifier using a structured output schema.

The interface (`classify_intent(text) → ClassificationResult`) is identical whether backed by keywords or an LLM, so swapping it requires no changes upstream.

### 2.3 Two-Tier Memory Architecture

**STM (Short-Term Memory)**
- Ring buffer of the 10 most recent conversation turns
- Pruned automatically via SQLite subquery — no application-level loop required
- Injected into every agent prompt to provide conversational continuity

**LTM (Long-Term Memory)**
- Significance-gated: only stored when `score ≥ 0.7`
- Significance scoring uses keyword presence as a proxy for importance
- Persists across sessions and is listed before STM in the context string

**Trade-off:** The significance scorer is simplistic. It cannot distinguish between a user mentioning "policy" in passing vs. asking a substantive policy question. A production system would use embedding similarity against a set of "important fact" templates, or ask the LLM to decide.

### 2.4 Append-Only Audit Log

The `audit_logs` table enforces append-only behaviour by convention:
- The `write_audit_log` function only ever executes `INSERT`
- No `UPDATE` or `DELETE` statements exist anywhere in the codebase
- In production, this could be enforced at the database level using SQLite triggers or PostgreSQL row-level security

### 2.5 Mock Agents vs. Real LLM Agents

All four sub-agents currently use deterministic mock responses.

**Reasons:**
- Allows the entire system to run without an OpenAI API key
- Makes tests fast, deterministic, and free
- The `run()` interface for every agent is identical (`async def run(user_message, context, timeout)`)

**Upgrade path:** Replace the `_mock_llm_response()` function in any agent with a LangChain `ChatOpenAI` call. The orchestrator, router, and tests require no changes.

### 2.6 SQLite Over PostgreSQL

SQLite was chosen because:
- Zero external dependencies — the system runs anywhere with Python
- Sufficient for the interview submission scope
- `aiosqlite` provides async access consistent with FastAPI's async model

**Trade-off:** SQLite does not support true concurrent writes. For a production system with multiple FastAPI workers, PostgreSQL with asyncpg would be appropriate.

### 2.7 Error Handling Strategy

Errors are handled at two levels:
1. **Agent level**: each agent retries up to `MAX_RETRIES` times with a per-attempt timeout
2. **API level**: a global FastAPI exception handler ensures raw Python tracebacks never reach the client

Users always receive a friendly, actionable error message.

---

## 3. Known Limitations

| Limitation | Impact | Mitigation Path |
|------------|--------|-----------------|
| Mock LLM responses | Responses are canned, not intelligent | Swap `_mock_llm_response` for `ChatOpenAI` call |
| Keyword classifier | Ambiguous phrasing may misclassify | Replace with LLM structured-output classifier |
| Simple significance scorer | May over/under-promote to LTM | Use embedding similarity scoring |
| SQLite concurrency | Write contention under parallel load | Migrate to PostgreSQL |
| No authentication | Any caller can read/write any user's memory | Add JWT auth middleware |
| No input sanitisation beyond Pydantic | SQL injection mitigated by parameterised queries, but no content filtering | Add content moderation layer |

---

## 4. What I Would Do With More Time

1. **Real LLM integration**: plug in `ChatOpenAI` with tool-calling for structured agent responses
2. **Vector-based LTM**: use sentence embeddings to store and retrieve semantically relevant memories rather than keyword-gated facts
3. **Conditional LangGraph routing**: branch the graph based on confidence score (e.g. always go to Clarification if confidence < 0.5, even mid-conversation)
4. **Authentication**: add user authentication so memory and audit logs are access-controlled
5. **Streaming responses**: use FastAPI's `StreamingResponse` with LangChain streaming to return agent tokens in real time

---

## 5. Challenges

- **LangGraph async compatibility**: LangGraph's `ainvoke` requires all node functions to be properly async. Mixing sync and async nodes caused subtle bugs that required careful wrapping.
- **SQLite in-memory for tests**: sharing an in-memory SQLite connection across async test fixtures required using `aiosqlite.connect(":memory:")` and ensuring `init_db()` ran before each test.
- **Append-only enforcement**: SQLite has no native append-only constraint. The solution was strict code discipline — a single `write_audit_log` function that only ever inserts, reviewed to confirm no other code path touches `audit_logs`.
