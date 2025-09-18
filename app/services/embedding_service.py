import requests
import numpy as np
from typing import List, Optional
import logging
from config.settings import OLLAMA_URL, EMBEDDING_MODEL

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.ollama_url = OLLAMA_URL
        self.model = EMBEDDING_MODEL

    async def check_model_availability(self) -> bool:
        """Check if the embedding model is available in Ollama."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                is_available = any(self.model in model for model in available_models)

                if not is_available:
                    logger.warning(f"Model {self.model} not found. Available models: {available_models}")
                    logger.warning(f"Please run: ollama pull {self.model}")

                return is_available
            return False
        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False

    async def generate_embedding(self, text: str) -> Optional[np.ndarray]:
        """Generate embedding for the given text using Ollama."""
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        try:
            payload = {
                "model": self.model,
                "prompt": text.strip()
            }

            response = requests.post(
                f"{self.ollama_url}/api/embeddings",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                embedding = np.array(data['embedding'], dtype=np.float32)
                logger.debug(f"Generated embedding of shape {embedding.shape} for text: {text[:50]}...")
                return embedding
            else:
                logger.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request to Ollama failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return None

    async def generate_embeddings_batch(self, texts: List[str]) -> List[Optional[np.ndarray]]:
        """Generate embeddings for multiple texts."""
        embeddings = []
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)

        return embeddings

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            dot_product = np.dot(vec1, vec2)
            norm_vec1 = np.linalg.norm(vec1)
            norm_vec2 = np.linalg.norm(vec2)

            if norm_vec1 == 0 or norm_vec2 == 0:
                return 0.0

            similarity = dot_product / (norm_vec1 * norm_vec2)
            return float(similarity)
        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {e}")
            return 0.0