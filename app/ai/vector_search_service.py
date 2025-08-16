from ..core.config import OPENAI_API_KEY
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from typing import List, Dict, Any

FAISS_INDEX_PATH = "data/faiss_index"

try:
    # Load embeddings and the vector store once when the module is imported
    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vector_store = FAISS.load_local(
        FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True
    )
except Exception as e:
    print(f"Could not load FAISS index. Run scripts/process_pdfs.py first. Error: {e}")
    vector_store = None


def semantic_search(query: str, k: int = 5) -> List[Dict[str, Any]]:
    """
    Performs a semantic search on the vector store and returns ranked results.
    """
    if vector_store is None:
        raise RuntimeError("Vector store is not available.")

    # FAISS returns documents and their L2 distance (lower is better)
    results_with_scores = vector_store.similarity_search_with_score(query, k=k)

    formatted_results = []
    for doc, score in results_with_scores:
        formatted_results.append(
            {"content": doc.page_content, "metadata": doc.metadata, "score": score}
        )

    return formatted_results
