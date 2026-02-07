import fitz  # PyMuPDF
import json
import re
from pathlib import Path


PDF_PATH = "data\policies\it_policy.pdf"
OUTPUT_PATH = "sample_output.json"


def clean_text(text):
    """
    Cleans raw PDF text:
    - Removes extra spaces
    - Removes page numbers
    - Normalizes line breaks
    """
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text


def extract_policy_text(pdf_path):
    """
    Extract text page by page with page numbers
    """
    doc = fitz.open(pdf_path)
    extracted = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        cleaned = clean_text(text)

        if cleaned:
            extracted.append({
                "page": page_num,
                "text": cleaned
            })

    return extracted


def save_output(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    policy_data = extract_policy_text(PDF_PATH)
    save_output(policy_data, OUTPUT_PATH)

    print(f"Ingestion complete. Pages extracted: {len(policy_data)}")
