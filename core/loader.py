from sentence_transformers import SentenceTransformer, CrossEncoder

from retrieval.hybrid_retrieval import hybrid_search
from retrieval.reranker import rerank
from LLM.compliance_reasoner import check_compliance

def load_engine():
    """
    This function is called ONLY once,
    AFTER FastAPI has started.
    """
    return check_compliance
