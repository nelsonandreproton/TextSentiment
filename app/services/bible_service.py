import re
import aiohttp
import logging
from typing import Optional, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class BibleVerse:
    book: str
    chapter: int
    verse: int
    text: str
    citation: str

class BibleService:
    def __init__(self):
        self.base_url = "https://bolls.life"
        self.default_translation = "ARA"  # Almeida Revista e Atualizada

        # Portuguese book names mapping to book numbers
        self.book_mapping = {
            # Old Testament
            "genesis": 1, "gênesis": 1, "gn": 1,
            "exodo": 2, "êxodo": 2, "ex": 2,
            "levitico": 3, "levítico": 3, "lv": 3,
            "numeros": 4, "números": 4, "nm": 4,
            "deuteronomio": 5, "deuteronômio": 5, "dt": 5,
            "josue": 6, "josué": 6, "js": 6,
            "juizes": 7, "juízes": 7, "jz": 7,
            "rute": 8, "rt": 8,
            "1 samuel": 9, "1samuel": 9, "1sm": 9, "1 sm": 9,
            "2 samuel": 10, "2samuel": 10, "2sm": 10, "2 sm": 10,
            "1 reis": 11, "1reis": 11, "1rs": 11, "1 rs": 11,
            "2 reis": 12, "2reis": 12, "2rs": 12, "2 rs": 12,
            "1 cronicas": 13, "1crônicas": 13, "1 crônicas": 13, "1cr": 13, "1 cr": 13,
            "2 cronicas": 14, "2crônicas": 14, "2 crônicas": 14, "2cr": 14, "2 cr": 14,
            "esdras": 15, "ed": 15,
            "neemias": 16, "ne": 16,
            "ester": 17, "et": 17,
            "jo": 18, "jó": 18,
            "salmos": 19, "sl": 19,
            "proverbios": 20, "provérbios": 20, "pv": 20,
            "eclesiastes": 21, "ec": 21,
            "cantares": 22, "canticos": 22, "cânticos": 22,
            "isaias": 23, "isaías": 23, "is": 23,
            "jeremias": 24, "jr": 24,
            "lamentacoes": 25, "lamentações": 25, "lm": 25,
            "ezequiel": 26, "ez": 26,
            "daniel": 27, "dn": 27,
            "oseias": 28, "oséias": 28,
            "joel": 29,
            "amos": 30, "amós": 30,
            "obadias": 31,
            "jonas": 32,
            "miqueias": 33,
            "naum": 34,
            "habacuque": 35,
            "sofonias": 36,
            "ageu": 37,
            "zacarias": 38,
            "malaquias": 39,

            # New Testament
            "mateus": 40, "mt": 40,
            "marcos": 41, "mc": 41,
            "lucas": 42, "lc": 42,
            "joao": 43, "joão": 43, "jo": 43,
            "atos": 44, "at": 44,
            "romanos": 45, "rm": 45,
            "1 corintios": 46, "1corintios": 46, "1 coríntios": 46, "1coríntios": 46, "1co": 46, "1 co": 46,
            "2 corintios": 47, "2corintios": 47, "2 coríntios": 47, "2coríntios": 47, "2co": 47, "2 co": 47,
            "galatas": 48, "gálatas": 48, "gl": 48,
            "efesios": 49, "efésios": 49, "ef": 49,
            "filipenses": 50,
            "colossenses": 51,
            "1 tessalonicenses": 52, "1tessalonicenses": 52,
            "2 tessalonicenses": 53, "2tessalonicenses": 53,
            "1 timoteo": 54, "1timóteo": 54, "1 timóteo": 54,
            "2 timoteo": 55, "2timóteo": 55, "2 timóteo": 55,
            "tito": 56,
            "filemom": 57, "filêmon": 57,
            "hebreus": 58,
            "tiago": 59,
            "1 pedro": 60, "1pedro": 60,
            "2 pedro": 61, "2pedro": 61,
            "1 joao": 62, "1joão": 62, "1 joão": 62,
            "2 joao": 63, "2joão": 63, "2 joão": 63,
            "3 joao": 64, "3joão": 64, "3 joão": 64,
            "judas": 65,
            "apocalipse": 66
        }

    def parse_citation(self, citation: str) -> Optional[Tuple[str, int, int]]:
        """
        Parse a Bible citation like 'Lucas 2,15' or 'João 3:16'
        Returns (book_name, chapter, verse) or None if invalid
        """
        try:
            # Clean the citation
            citation = citation.strip().lower()

            # Handle different separators (comma, colon, period)
            # Patterns: "Lucas 2,15", "João 3:16", "Mateus 5.3"
            patterns = [
                r'^(.+?)\s+(\d+)[,:.](\d+)$',  # "book chapter,verse"
                r'^(.+?)\s+(\d+)\s+(\d+)$',    # "book chapter verse"
            ]

            for pattern in patterns:
                match = re.match(pattern, citation)
                if match:
                    book_name = match.group(1).strip()
                    chapter = int(match.group(2))
                    verse = int(match.group(3))

                    # Validate book name
                    if book_name in self.book_mapping:
                        return book_name, chapter, verse

            return None

        except (ValueError, AttributeError):
            return None

    async def get_verse(self, book_name: str, chapter: int, verse: int, translation: str = None) -> Optional[BibleVerse]:
        """
        Get a Bible verse from the API
        """
        try:
            if translation is None:
                translation = self.default_translation

            # Get book number
            book_number = self.book_mapping.get(book_name.lower())
            if not book_number:
                logger.error(f"Unknown book name: {book_name}")
                return None

            # Make API request
            url = f"{self.base_url}/get-verse/{translation}/{book_number}/{chapter}/{verse}/"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        logger.error(f"Bible API error {response.status} for {book_name} {chapter}:{verse}")
                        return None

                    data = await response.json()

                    if not data or 'text' not in data:
                        logger.error(f"Invalid response from Bible API for {book_name} {chapter}:{verse}")
                        return None

                    # Create citation string
                    citation = f"{book_name.title()} {chapter}:{verse}"

                    return BibleVerse(
                        book=book_name.title(),
                        chapter=chapter,
                        verse=verse,
                        text=data['text'],
                        citation=citation
                    )

        except Exception as e:
            logger.error(f"Failed to get Bible verse {book_name} {chapter}:{verse}: {e}")
            return None

    async def get_verse_by_citation(self, citation: str, translation: str = None) -> Optional[BibleVerse]:
        """
        Get a Bible verse by citation string like 'Lucas 2,15'
        """
        parsed = self.parse_citation(citation)
        if not parsed:
            logger.error(f"Failed to parse citation: {citation}")
            return None

        book_name, chapter, verse = parsed
        return await self.get_verse(book_name, chapter, verse, translation)

    def is_bible_citation(self, text: str) -> bool:
        """
        Check if the text looks like a Bible citation
        """
        return self.parse_citation(text) is not None

    async def test_connection(self) -> bool:
        """
        Test if the Bible API is accessible
        """
        try:
            # Test with a simple verse (Genesis 1:1)
            test_verse = await self.get_verse("genesis", 1, 1)
            return test_verse is not None
        except Exception as e:
            logger.error(f"Bible API test failed: {e}")
            return False