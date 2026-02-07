import json
import re
from pathlib import Path

INPUT_PATH = "sample_output.json"
OUTPUT_PATH = "clauses.json"


def split_into_sentences(text):
    """
    Basic sentence splitter.
    Good enough for policy text.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s.strip()) > 30]


def is_policy_clause(sentence):
    """
    Heuristic to detect policy-like clauses
    """
    keywords = [
        "must",
        "shall",
        "must not",
        "shall not",
        "required",
        "prohibited",
        "may not"
    ]
    s = sentence.lower()
    return any(k in s for k in keywords)


def extract_clauses(pages):
    clauses = []
    clause_id = 1

    for page in pages:
        page_num = page["page"]
        sentences = split_into_sentences(page["text"])

        for sent in sentences:
            if is_policy_clause(sent):
                clauses.append({
                    "clause_id": f"IT-SEC-{clause_id:03d}",
                    "page": page_num,
                    "text": sent
                })
                clause_id += 1

    return clauses


def save_output(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        pages = json.load(f)

    clauses = extract_clauses(pages)
    save_output(clauses, OUTPUT_PATH)

    print(f"Clause extraction complete. Clauses found: {len(clauses)}")
