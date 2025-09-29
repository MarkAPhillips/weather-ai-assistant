import weaviate
from weaviate.auth import AuthApiKey
import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class WeaviateService:
    """Service for interacting with Weaviate vector database."""
    def __init__(self):
        """Initialize Weaviate client."""
        # Get Weaviate credentials from environment variables
        self.cluster_url = os.getenv('WEAVIATE_CLUSTER_URL')
        self.api_key = os.getenv('WEAVIATE_API_KEY')
        self.client = None

        if not self.cluster_url or not self.api_key:
            logger.warning(
                "Weaviate credentials not found. "
                "Skipping Weaviate initialisation."
            )
            return

        try:
            # Initialize Weaviate client (v4 syntax)
            # Ensure URL has https protocol
            cluster_url = self.cluster_url
            if cluster_url and not cluster_url.startswith('https://'):
                cluster_url = f"https://{cluster_url}"

            self.client = weaviate.connect_to_weaviate_cloud(
                cluster_url=cluster_url,
                auth_credentials=AuthApiKey(api_key=self.api_key),
                skip_init_checks=True
            )

            # Create schema if it doesn't exist
            self._create_schema()
            logger.info("Weaviate client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Weaviate client: {e}")
            self.client = None

    def __del__(self):
        """Cleanup method to close Weaviate connection."""
        self.close()

    def close(self):
        """Close the Weaviate connection."""
        if self.client:
            try:
                self.client.close()
                logger.info("Weaviate connection closed")
            except Exception as e:
                logger.warning(f"Error closing Weaviate connection: {e}")
            finally:
                self.client = None

    def _create_schema(self):
        """Create the weather knowledge schema in Weaviate."""
        if not self.client:
            return

        # Check if schema already exists
        try:
            existing_classes = self.client.collections.get_all()
            if any([cls.name == 'WeatherKnowledge'
                   for cls in existing_classes.values()]):
                logger.info("WeatherKnowledge collection already exists")
                return
        except Exception as e:
            logger.warning(f"Error checking existing collections: {e}")
        # Schema is defined inline in the collection creation
        try:
            # Check if collection already exists
            try:
                self.client.collections.get("WeatherKnowledge")
                logger.info("WeatherKnowledge collection already exists")
                return
            except Exception:
                pass

            # Try to create collection - this might fail due to permissions
            try:
                self.client.collections.create(name="WeatherKnowledge")
                logger.info("WeatherKnowledge collection created successfully")
            except Exception as create_error:
                logger.warning(
                    f"Cannot create collection (likely permissions issue): "
                    f"{create_error}"
                )
                logger.info(
                    "WeatherKnowledge collection will need to be created "
                    "manually in Weaviate dashboard"
                )
        except Exception as e:
            logger.error(f"Error setting up schema: {e}")

    def add_weather_knowledge(self,
                              content: str,
                              title: str = "",
                              category: str = "",
                              location: str = "",
                              season: str = "",
                              weather_type: str = "") -> bool:
        """Add weather knowledge to the vector database."""
        if not self.client:
            return False

        try:
            self.client.collections.get("WeatherKnowledge").data.create({
                "content": content,
                "title": title,
                "category": category,
                "location": location,
                "season": season,
                "weather_type": weather_type
            })

            logger.info(f"Added weather knowledge: {title}")
            return True
        except Exception as e:
            logger.error(f"Error adding weather knowledge: {e}")
            return False

    def search_weather_knowledge(self, query: str,
                                 limit: int = 3) -> List[Dict[str, Any]]:
        """Search weather knowledge using keyword-based text search."""
        if not self.client:
            return []

        try:
            collection = self.client.collections.get("WeatherKnowledge")

            # Use HTTP-only search without vectorization
            result = collection.query.fetch_objects(limit=limit)

            if result.objects:
                knowledge_items = []
                query_lower = query.lower()
                # Filter results that match our query keywords
                for obj in result.objects:
                    content = obj.properties.get("content", "").lower()
                    title = obj.properties.get("title", "").lower()
                    # Simple keyword matching
                    if (query_lower in content or
                            query_lower in title or
                            any(word in content
                                for word in query_lower.split())):
                        knowledge_items.append({
                            "content": obj.properties.get("content", ""),
                            "title": obj.properties.get("title", ""),
                            "category": obj.properties.get("category", ""),
                            "location": obj.properties.get("location", ""),
                            "season": obj.properties.get("season", ""),
                            "weather_type": obj.properties.get(
                                "weather_type", ""
                            )
                        })
                logger.info(
                    f"Found {len(knowledge_items)} weather knowledge items "
                    f"for query: {query}"
                )
                return knowledge_items
            else:
                logger.info(f"No weather knowledge found for query: {query}")
                return []
        except Exception as e:
            logger.error(f"Error searching weather knowledge: {e}")
            return []

    def batch_add_knowledge(self,
                            knowledge_items: List[Dict[str, str]]) -> int:
        """Add multiple weather knowledge items in batch."""
        if not self.client:
            return 0
        success_count = 0
        try:
            collection = self.client.collections.get("WeatherKnowledge")
            collection.data.insert_many(knowledge_items)
            success_count = len(knowledge_items)
            logger.info(
                f"Successfully added {success_count} weather knowledge items"
            )
        except Exception as e:
            logger.error(f"Error in batch adding knowledge: {e}")
        return success_count

    def health_check(self) -> bool:
        """Check if Weaviate is accessible."""
        if not self.client:
            return False
        try:
            # Try to list collections to verify connection
            self.client.collections.list_all()
            return True
        except Exception as e:
            logger.error(f"Weaviate health check failed: {e}")
            return False
