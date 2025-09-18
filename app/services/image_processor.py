import re
from pathlib import Path
from typing import Dict
import logging
from .vision_ocr import VisionOCR

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.musical_notes_pattern = r'\b(Re|Sol|Do|Mi|Fa|La|Si)-?\b'
        self.vision_ocr = VisionOCR()


    def remove_corner_numbers(self, text: str, image_shape=None) -> str:
        """Remove numbers that appear in corners of the image."""
        lines = text.split('\n')
        # Remove lines that are just numbers or contain only digits and spaces
        filtered_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            # Skip lines that are just numbers
            if re.match(r'^\d+[\s\d]*$', stripped):
                continue
            filtered_lines.append(line)

        return '\n'.join(filtered_lines)

    def filter_musical_notes(self, text: str) -> str:
        """Remove Portuguese musical note references."""
        # Remove musical notes pattern
        text = re.sub(self.musical_notes_pattern, '', text, flags=re.IGNORECASE)
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


    async def process_image(self, image_path: Path) -> Dict[str, str]:
        """Main processing pipeline for extracting title and text from image using vision model."""
        try:
            logger.info(f"Processing image with vision model: {image_path}")

            # Use vision model to extract title and content directly
            extracted = await self.vision_ocr.extract_text_from_image(image_path)

            title = extracted['title'].strip()
            content = extracted['content'].strip()

            logger.info(f"Vision model extracted - Title: '{title}', Content length: {len(content)}")

            # Apply text filtering
            if content:
                content = self.remove_corner_numbers(content)
                content = self.filter_musical_notes(content)

            # Clean up text
            title = ' '.join(title.split())
            content = ' '.join(content.split())

            logger.info(f"Final processed - Title: '{title}', Content length: {len(content)}")

            return {
                'title': title,
                'content': content
            }

        except Exception as e:
            logger.error(f"Vision model processing failed: {e}")
            raise Exception(f"Vision model OCR failed: {e}")