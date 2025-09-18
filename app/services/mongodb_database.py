import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, TEXT
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime
from config.settings import MONGODB_URL, MONGODB_DATABASE
import logging

logger = logging.getLogger(__name__)

class MongoDatabase:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None

    async def connect(self):
        """Establish database connection."""
        try:
            self.client = AsyncIOMotorClient(MONGODB_URL)
            self.db = self.client[MONGODB_DATABASE]
            self.collection = self.db.text_records

            # Test connection
            await self.client.admin.command('ping')
            logger.info("MongoDB connection established")

            # Create indexes
            await self.create_indexes()

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def create_indexes(self):
        """Create necessary indexes for the collection."""
        try:
            # Create text index for title search
            title_index = IndexModel([("title", TEXT)], name="title_text_index")

            # Create index for created_at
            date_index = IndexModel([("created_at", -1)], name="created_at_index")

            # Create compound index for title uniqueness (case-insensitive)
            title_unique_index = IndexModel([("title_lower", 1)], unique=True, name="title_unique_index")

            await self.collection.create_indexes([title_index, date_index, title_unique_index])
            logger.info("MongoDB indexes created successfully")

        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            # Don't raise - indexes might already exist

    async def check_title_exists(self, title: str) -> Optional[Dict]:
        """Check if a record with the given title already exists (case-insensitive)."""
        if self.collection is None:
            await self.connect()

        try:
            # Search using lowercase title for case-insensitive comparison
            result = await self.collection.find_one({
                "title_lower": title.lower().strip()
            })

            if result:
                # Convert ObjectId to string for JSON serialization
                result["id"] = str(result["_id"])
                result.pop("_id", None)
                return result
            return None

        except Exception as e:
            logger.error(f"Failed to check title existence: {e}")
            raise

    async def insert_record(self, title: str, text: str, embedding: np.ndarray, filename: Optional[str]) -> str:
        """Insert a new text record with embedding."""
        if self.collection is None:
            await self.connect()

        try:
            document = {
                "title": title,
                "title_lower": title.lower().strip(),  # For case-insensitive uniqueness
                "extracted_text": text,
                "embedding": embedding.tolist(),  # Convert numpy array to list
                "image_filename": filename,
                "created_at": datetime.utcnow(),
                "word_count": len(text.split()),
                "character_count": len(text)
            }

            result = await self.collection.insert_one(document)
            record_id = str(result.inserted_id)

            logger.info(f"Inserted record {record_id}: {title[:50]}...")
            return record_id

        except Exception as e:
            logger.error(f"Failed to insert record: {e}")
            raise

    async def search_similar(self, query_embedding: np.ndarray, limit: int = 10) -> List[Dict]:
        """Find records with similar embeddings using cosine similarity."""
        if self.collection is None:
            await self.connect()

        # Validate and sanitize limit parameter
        limit = max(1, min(limit, 100))

        try:
            # Get all records with embeddings
            cursor = self.collection.find(
                {"embedding": {"$exists": True, "$ne": None}},
                {"_id": 1, "title": 1, "extracted_text": 1, "image_filename": 1,
                 "created_at": 1, "embedding": 1}
            )

            results = []
            query_embedding_list = query_embedding.tolist()

            async for doc in cursor:
                # Calculate cosine similarity
                doc_embedding = np.array(doc["embedding"])
                similarity_score = self._cosine_similarity(query_embedding, doc_embedding)

                # Format result
                result = {
                    "id": str(doc["_id"]),
                    "title": doc["title"],
                    "extracted_text": doc["extracted_text"],
                    "image_filename": doc["image_filename"],
                    "similarity_score": float(similarity_score),
                    "created_at": doc["created_at"]
                }
                results.append(result)

            # Sort by similarity score (descending) and limit results
            results.sort(key=lambda x: x["similarity_score"], reverse=True)
            return results[:limit]

        except Exception as e:
            logger.error(f"Failed to search similar records: {e}")
            raise

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
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

    async def get_all_records(self) -> List[Dict]:
        """Get all text records."""
        if self.collection is None:
            await self.connect()

        try:
            cursor = self.collection.find(
                {},
                {"_id": 1, "title": 1, "extracted_text": 1, "image_filename": 1, "created_at": 1}
            ).sort("created_at", -1)

            results = []
            async for doc in cursor:
                result = {
                    "id": str(doc["_id"]),
                    "title": doc["title"],
                    "extracted_text": doc["extracted_text"],
                    "image_filename": doc["image_filename"],
                    "created_at": doc["created_at"]
                }
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Failed to get all records: {e}")
            raise

    async def get_record_by_id(self, record_id: str) -> Optional[Dict]:
        """Get a specific record by ID."""
        if self.collection is None:
            await self.connect()

        try:
            from bson import ObjectId

            doc = await self.collection.find_one({"_id": ObjectId(record_id)})
            if doc:
                # Convert ObjectId to string and calculate stats
                result = {
                    "id": str(doc["_id"]),
                    "title": doc["title"],
                    "extracted_text": doc["extracted_text"],
                    "image_filename": doc["image_filename"],
                    "created_at": doc["created_at"],
                    "word_count": doc.get("word_count", len(doc["extracted_text"].split())),
                    "character_count": doc.get("character_count", len(doc["extracted_text"]))
                }
                return result
            return None

        except Exception as e:
            logger.error(f"Failed to get record {record_id}: {e}")
            raise

    async def update_record(self, record_id: str, title: str, text: str, embedding: np.ndarray) -> bool:
        """Update a text record by ID."""
        if self.collection is None:
            await self.connect()

        try:
            from bson import ObjectId

            update_data = {
                "title": title,
                "title_lower": title.lower().strip(),
                "extracted_text": text,
                "embedding": embedding.tolist(),
                "word_count": len(text.split()),
                "character_count": len(text),
                "updated_at": datetime.utcnow()
            }

            result = await self.collection.update_one(
                {"_id": ObjectId(record_id)},
                {"$set": update_data}
            )

            if result.modified_count > 0:
                logger.info(f"Updated record {record_id}: {title[:50]}...")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to update record {record_id}: {e}")
            raise

    async def delete_record(self, record_id: str) -> bool:
        """Delete a text record by ID."""
        if self.collection is None:
            await self.connect()

        try:
            from bson import ObjectId

            result = await self.collection.delete_one({"_id": ObjectId(record_id)})

            if result.deleted_count > 0:
                logger.info(f"Deleted record {record_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to delete record {record_id}: {e}")
            raise

    def close(self):
        """Close database connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")