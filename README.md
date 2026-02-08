# VeriClause

VeriClause is a policy compliance decision engine built using Retrieval-Augmented Generation (RAG).
Unlike chat-based RAG systems, VeriClause focuses on **auditable, clause-grounded decisions** with verification and confidence scoring.

---

## Problem
Organizations need to evaluate whether user actions comply with internal policies.
Pure LLM-based solutions are unreliable due to hallucinations and lack of traceability.

---

## Solution
VeriClause combines deterministic retrieval with controlled LLM reasoning:
- Clause-level policy ingestion for auditability
- Hybrid retrieval (BM25 + embeddings) for high recall
- Cross-encoder re-ranking for precision
- Local LLM reasoning using Ollama
- Verification layer to prevent hallucinations
- Confidence calibration for safe escalation

---

## How VeriClause Differs from Typical RAG Systems
- Designed for **decision-making**, not chat
- LLM is not the source of truth
- Every decision is traceable to policy clauses
- Ambiguous cases escalate instead of guessing

---

## Architecture
1. Policy PDFs are ingested and split into enforceable clauses
2. Clauses are embedded and indexed using FAISS
3. Queries use hybrid retrieval + re-ranking
4. LLM reasons only over retrieved clauses
5. A verifier checks grounding and adjusts confidence
6. FastAPI exposes a secure, stateless decision API

---

## Confidence Interpretation
- **> 0.8** → Strong evidence, auto-decision
- **0.5 – 0.8** → Evidence present, caution advised
- **< 0.5** → Insufficient evidence, needs human review

---

## Security & Data Privacy
- Uses a local LLM (Ollama); no data leaves the machine
- Only retrieved policy clauses are shared with the model
- Stateless API design with strict input validation

---

## Tech Stack
- Python
- FastAPI
- FAISS
- SentenceTransformers
- Cross-Encoder Re-ranking
- Ollama (local LLM)
- Pydantic

---

## API Example
POST `/check-compliance`
```json
{
  "scenario": "An employee shared their VPN password with a colleague."
}
