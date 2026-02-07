import requests
import json
from retrieval.reranker import rerank
from LLM.verifier import verify_decision


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"


def call_ollama(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature":0.1
    }

    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()

    return response.json()["response"]


def build_prompt(query, clauses):
    context = "\n".join(
        [f"- ({c['clause_id']}) {c['text']}" for c in clauses]
    )

    prompt = f"""
You are a policy compliance engine.

ONLY use the policy clauses below.
Do NOT make assumptions.
If evidence is insufficient, say NEEDS_REVIEW.

Policy Clauses:
{context}

Scenario:
{query}

Return output in STRICT JSON with this schema:
{{
  "status": "COMPLIANT | NON_COMPLIANT | NEEDS_REVIEW",
  "violations": [],
  "justification": [],
  "confidence": 0.0
}}
"""
    return prompt.strip()


def check_compliance(query):
    clauses = rerank(query)

    if not clauses:
        return {
            "status": "NEEDS_REVIEW",
            "violations": [],
            "justification": ["No relevant policy clauses found"],
            "confidence": 0.2
        }

    prompt = build_prompt(query, clauses)
    raw_output = call_ollama(prompt)

    try:
        llm_result = json.loads(raw_output)
    except json.JSONDecodeError:
        return {
            "status": "NEEDS_REVIEW",
            "violations": [],
            "justification": ["LLM output could not be parsed"],
            "confidence": 0.1
        }

    # ---- VERIFICATION STEP (DAY 8) ----
    verification = verify_decision(query, clauses, llm_result)

    if not verification["supported"]:
        llm_result["status"] = "NEEDS_REVIEW"
        llm_result["confidence"] = max(
            0.0,
            llm_result.get("confidence", 0.5) + verification["confidence_adjustment"]
        )
        llm_result["justification"].append(
            "Decision downgraded due to insufficient evidence"
        )
        return llm_result

    # Adjust confidence if needed
    llm_result["confidence"] = max(
        0.0,
        min(1.0, llm_result.get("confidence", 0.7) + verification["confidence_adjustment"])
    )

    return llm_result

# -------------------------------
# Test run
# -------------------------------
if __name__ == "__main__":
    scenario = "An employee shared their password with a colleague."
    result = check_compliance(scenario)
    print(json.dumps(result, indent=2))
