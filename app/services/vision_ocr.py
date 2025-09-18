import base64
import json
import logging
from pathlib import Path
from typing import Dict, Optional
import aiohttp
import asyncio
from PIL import Image, ImageEnhance, ImageOps
import io
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class VisionOCR:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "moondream:1.8b"):
        self.ollama_url = ollama_url
        self.model = model  # Default to LLaVA for better accuracy

    def _preprocess_image(self, image_path: Path) -> Image.Image:
        """Enhanced preprocessing to improve text visibility for Portuguese characters."""
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Enhanced contrast for better text visibility
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)  # Stronger contrast boost

            # Enhanced sharpness for clearer character definition
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.5)  # More sharpness for Portuguese diacritics

            # Brightness adjustment to ensure good contrast
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(1.1)  # Slight brightness boost

            logger.info("Image preprocessed: enhanced contrast, sharpness, and brightness for Portuguese text")
            return img

    def _encode_image_to_base64(self, image_path: Path) -> str:
        """Convert and preprocess image to base64 string for API."""
        try:
            # Preprocess the image first
            img = self._preprocess_image(image_path)

            # Resize if image is very large
            max_size = 768
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

            # Convert to bytes
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=95)
            buffer.seek(0)

            # Encode to base64
            image_bytes = buffer.getvalue()
            return base64.b64encode(image_bytes).decode('utf-8')

        except Exception as e:
            logger.error(f"Failed to encode image: {e}")
            raise

    async def extract_text_from_image(self, image_path: Path) -> Dict[str, str]:
        """Extract title and content from image."""
        try:
            # Encode image
            base64_image = self._encode_image_to_base64(image_path)

            # Prepare the prompt for text extraction
            prompt = """Analyze this image and extract all Portuguese text you see. The image has a red bold title at the top and black text content below it.

Extract the actual text preserving Portuguese accents and special characters (ç, ã, õ, é, í, ú, á, ó).

Respond with JSON:
{"title": "actual red title from image", "content": "actual black text from image"}"""

            # Prepare API request
            payload = {
                "model": self.model,
                "prompt": prompt,
                "images": [base64_image],
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Very low but not zero for Portuguese diacritics
                    "top_p": 0.2,        # Slightly more focused sampling for character variants
                    "top_k": 5,          # Allow some variation for accented characters
                    "num_predict": 3000, # More tokens for Portuguese text content
                    "repeat_penalty": 1.0  # No penalty to allow repeated words if they exist
                }
            }

            # Make API call
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Ollama API error {response.status}: {error_text}")

                    result = await response.json()
                    raw_response = result.get('response', '').strip()

                    logger.info(f"Moondream raw response: {raw_response[:200]}...")

                    # Try to parse JSON response
                    try:
                        # Look for JSON in the response
                        json_start = raw_response.find('{')
                        json_end = raw_response.rfind('}') + 1

                        if json_start != -1 and json_end > json_start:
                            json_str = raw_response[json_start:json_end]
                            parsed = json.loads(json_str)

                            title = parsed.get('title', '').strip()
                            content = parsed.get('content', '').strip()

                            logger.info(f"Moondream extracted - Title: '{title}', Content length: {len(content)}")

                            return {
                                'title': title,
                                'content': content
                            }
                        else:
                            raise ValueError("No valid JSON found in response")

                    except (json.JSONDecodeError, ValueError) as e:
                        logger.warning(f"Failed to parse JSON response: {e}")

                        # Fallback: try to extract text manually from the response
                        lines = raw_response.split('\n')
                        title = ""
                        content = ""

                        # Look for title and content indicators
                        for line in lines:
                            line = line.strip()
                            if 'title' in line.lower() and ':' in line:
                                title = line.split(':', 1)[1].strip().strip('"')
                            elif 'content' in line.lower() and ':' in line:
                                content = line.split(':', 1)[1].strip().strip('"')

                        # If manual extraction failed, use the entire response as content
                        if not title and not content:
                            content = raw_response
                            title = "Extracted Text"  # Fallback title

                        logger.info(f"Fallback extraction - Title: '{title}', Content length: {len(content)}")

                        return {
                            'title': title,
                            'content': content
                        }

        except Exception as e:
            logger.error(f"Vision OCR failed: {e}")
            if "timeout" in str(e).lower():
                raise Exception(f"Vision model timed out after 120 seconds. The model may be busy or the image too complex.")
            elif "connection" in str(e).lower():
                raise Exception(f"Could not connect to Ollama server. Make sure Ollama is running.")
            else:
                raise Exception(f"Vision model error: {e}")

    async def test_connection(self) -> bool:
        """Test if Ollama and moondream model are available."""
        try:
            async with aiohttp.ClientSession() as session:
                # Check if Ollama is running
                async with session.get(f"{self.ollama_url}/api/tags", timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        return False

                    # Check if moondream model is available
                    models = await response.json()
                    model_names = [model['name'] for model in models.get('models', [])]

                    if self.model not in model_names:
                        logger.error(f"Model {self.model} not found. Available models: {model_names}")
                        return False

                    logger.info(f"Moondream OCR service ready with model: {self.model}")
                    return True

        except Exception as e:
            logger.error(f"Moondream OCR test failed: {e}")
            return False