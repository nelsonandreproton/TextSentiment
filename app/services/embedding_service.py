import requests
import numpy as np
import time
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
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                is_available = any(self.model in model for model in available_models)

                if not is_available:
                    logger.warning(f"Model {self.model} not found. Available models: {available_models}")
                    logger.warning(f"Please run: ollama pull {self.model}")
                else:
                    logger.info(f"✅ Model {self.model} is available")

                return is_available
            else:
                logger.error(f"Failed to connect to Ollama API. Status code: {response.status_code}")
                return False
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout connecting to Ollama API: {e}")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to Ollama API at {self.ollama_url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to check model availability: {e}")
            return False

    async def warm_up_model(self) -> bool:
        """Warm up the model by generating a test embedding."""
        try:
            logger.info(f"🔥 Warming up model {self.model}...")
            # Use shorter timeout for warm-up to avoid blocking startup
            test_embedding = await self.generate_embedding("test", retries=0)
            if test_embedding is not None:
                logger.info(f"✅ Model {self.model} warmed up successfully")
                return True
            else:
                logger.warning(f"⚠️ Model warm-up failed - will try on first actual request")
                return False
        except Exception as e:
            logger.warning(f"Model warm-up failed: {e} - will try on first actual request")
            return False

    async def generate_embedding(self, text: str, retries: int = 2) -> Optional[np.ndarray]:
        """Generate embedding for the given text using Ollama."""
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        text = text.strip()

        for attempt in range(retries + 1):
            try:
                payload = {
                    "model": self.model,
                    "prompt": text
                }

                # Progressive timeout: shorter for retries
                timeout = 180 if attempt == 0 else 60
                logger.debug(f"Attempt {attempt + 1}: Requesting embedding for {len(text)} chars with {timeout}s timeout")

                start_time = time.time()
                response = requests.post(
                    f"{self.ollama_url}/api/embeddings",
                    json=payload,
                    timeout=timeout
                )
                request_time = time.time() - start_time

                if response.status_code == 200:
                    data = response.json()
                    embedding = np.array(data['embedding'], dtype=np.float32)
                    logger.info(f"✅ Generated embedding of shape {embedding.shape} in {request_time:.2f}s for text: {text[:50]}...")
                    return embedding
                else:
                    logger.error(f"Ollama API error (attempt {attempt + 1}): {response.status_code} - {response.text}")
                    if attempt < retries:
                        logger.info(f"Retrying embedding generation... (attempt {attempt + 2})")
                        continue
                    return None

            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
                if attempt < retries:
                    logger.info(f"Retrying embedding generation... (attempt {attempt + 2})")
                    continue
                logger.error(f"All attempts failed due to timeout. Text length: {len(text)} characters")
                return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Request to Ollama failed (attempt {attempt + 1}): {e}")
                if attempt < retries:
                    logger.info(f"Retrying embedding generation... (attempt {attempt + 2})")
                    continue
                return None
            except Exception as e:
                logger.error(f"Failed to generate embedding (attempt {attempt + 1}): {e}")
                if attempt < retries:
                    logger.info(f"Retrying embedding generation... (attempt {attempt + 2})")
                    continue
                return None

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