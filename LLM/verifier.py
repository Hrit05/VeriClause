import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"


def call_ollama(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,
            "num_predict": 200
        }
    }
    res = requests.post(OLLAMA_URL, json=payload)
    res.raise_for_status()
    return res.json()["response"]


def build_verification_prompt(query, clauses, llm_output):
    clause_text = "\n".join(
        [f"- ({c['clause_id']}) {c['text']}" for c in clauses]
    )

    prompt = f"""
You are a verification engine.

Your job is to CHECK the LLM decision below.
Do NOT make new arguments.
Do NOT introduce new rules.

Policy Clauses:
{clause_text}

Scenario:
{query}

LLM Decision:
{json.dumps(llm_output, indent=2)}

Answer in STRICT JSON:
{{
  "supported": true | false,
  "issues": [],
  "confidence_adjustment": -0.5 to 0.0
}}

Rules:
- supported = false if any claim is not directly supported by clauses
- confidence_adjustment is negative if evidence is weak or ambiguous
"""
    return prompt.strip()


def verify_decision(query, clauses, llm_output):
    prompt = build_verification_prompt(query, clauses, llm_output)
    raw = call_ollama(prompt)

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "supported": False,
            "issues": ["Verifier output could not be parsed"],
            "confidence_adjustment": -0.25
        }
