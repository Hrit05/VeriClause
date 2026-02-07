VERICLAUSE
"Clause-level IT Policy Compliance System using LLM APIs and Retrieval-Augmented Generation"

INPUT:


For output:
{
  "status": "COMPLIANT | NON_COMPLIANT | NEEDS_REVIEW",
  "violations": [],
  "policy_clauses": [],
  "explanation": [],
  "confidence": 0.0
}
Hard Rules:

LLM can only reason on retrieved clauses
Every violation must map to a clause ID
Missing info → NEEDS_REVIEW
No free-text answers allowed

❌ Out of Scope
Legal advice
Policy interpretation beyond text
Employee intent analysis
Chat or conversation memory
Multi-policy aggregation (for now)


Architecture:
Scenario
 ↓
Retriever (policy clauses)
 ↓
Re-ranker
 ↓
LLM Reasoning
 ↓
Verification
 ↓
JSON Output
