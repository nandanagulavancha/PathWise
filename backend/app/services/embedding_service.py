import google.generativeai as genai
from app.config import get_settings


class EmbeddingService:
    def __init__(self):
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)

    def generate_embedding(self, text: str) -> list[float]:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document",
        )
        return result["embedding"]

    def generate_query_embedding(self, text: str) -> list[float]:
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_query",
        )
        return result["embedding"]

    def compute_similarity(self, embedding1: list[float], embedding2: list[float]) -> float:
        if not embedding1 or not embedding2:
            return 0.0
        dot = sum(a * b for a, b in zip(embedding1, embedding2))
        norm1 = sum(a * a for a in embedding1) ** 0.5
        norm2 = sum(b * b for b in embedding2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)
