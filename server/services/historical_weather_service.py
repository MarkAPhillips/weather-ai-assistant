"""
Historical Weather Events Service for Weaviate Integration
Handles EM-DAT historical weather events data
"""

import weaviate
from weaviate.auth import AuthApiKey
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class HistoricalWeatherService:
    """Service for managing historical weather events in Weaviate."""

    def __init__(self):
        """Initialize Historical Weather Service with Weaviate client."""
        # Get Weaviate credentials from environment variables
        self.cluster_url = os.getenv('WEAVIATE_CLUSTER_URL')
        self.api_key = os.getenv('WEAVIATE_API_KEY')
        self.client = None

        if not self.cluster_url or not self.api_key:
            logger.warning(
                "Weaviate credentials not found. "
                "Skipping Historical Weather Service initialization."
            )
            return

        try:
            # Initialize Weaviate client (v4 syntax)
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
            logger.info("Historical Weather Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Historical Weather Service: {e}")
            self.client = None

    def __del__(self):
        """Cleanup method to close Weaviate connection."""
        self.close()

    def close(self):
        """Close the Weaviate connection."""
        if self.client:
            try:
                self.client.close()
                logger.info("Historical Weather Service connection closed")
            except Exception as e:
                logger.warning(f"Error closing Historical Weather Service connection: {e}")
            finally:
                self.client = None

    def _create_schema(self):
        """Create the HistoricalWeatherEvent schema in Weaviate."""
        if not self.client:
            return

        try:
            # Check if collection already exists
            try:
                self.client.collections.get("HistoricalWeatherEvent")
                logger.info("HistoricalWeatherEvent collection already exists")
                return
            except Exception:
                pass

            # Create the collection with schema
            try:
                self.client.collections.create(
                    name="HistoricalWeatherEvent",
                    properties=[
                        weaviate.classes.config.Property(
                            name="event_id",
                            data_type=weaviate.classes.config.DataType.TEXT,
                            description="Unique event identifier from EM-DAT"
                        ),
                        weaviate.classes.config.Property(
                            name="event_name",
                            data_type=weaviate.classes.config.DataType.TEXT,
                            description="Name of the weather event"
                        ),
                        weaviate.classes.config.Property(
                            name="country",
                            data_type=weaviate.classes.config.DataType.TEXT,
                            description="Country where event occurred"
                        ),
                        weaviate.classes.config.Property(
                            name="location",
                            data_type=weaviate.classes.config.DataType.TEXT,
                            description="Specific location details"
                        ),
                        weaviate.classes.config.Property(
                            name="event_type",
                            data_type=weaviate.classes.config.DataType.TEXT,
                            description="Main event type (Storm, Extreme temperature, etc.)"
                        ),
                        weaviate.classes.config.Property(
                            name="event_subtype",
                            data_type=weaviate.classes.config.DataType.TEXT,
                            description="Specific event subtype (Tropical cyclone, Heat wave, etc.)"
                        ),
                        weaviate.classes.config.Property(
                            name="start_date",
                            data_type=weaviate.classes.config.DataType.DATE,
                            description="Event start date"
                        ),
                        weaviate.classes.config.Property(
                            name="end_date",
                            data_type=weaviate.classes.config.DataType.DATE,
                            description="Event end date"
                        ),
                        weaviate.classes.config.Property(
                            name="fatalities",
                            data_type=weaviate.classes.config.DataType.NUMBER,
                            description="Number of fatalities"
                        ),
                        weaviate.classes.config.Property(
                            name="affected",
                            data_type=weaviate.classes.config.DataType.NUMBER,
                            description="Number of people affected"
                        ),
                        weaviate.classes.config.Property(
                            name="damage_usd",
                            data_type=weaviate.classes.config.DataType.NUMBER,
                            description="Economic damage in USD"
                        ),
                        weaviate.classes.config.Property(
                            name="latitude",
                            data_type=weaviate.classes.config.DataType.NUMBER,
                            description="Geographic latitude"
                        ),
                        weaviate.classes.config.Property(
                            name="longitude",
                            data_type=weaviate.classes.config.DataType.NUMBER,
                            description="Geographic longitude"
                        ),
                        weaviate.classes.config.Property(
                            name="magnitude",
                            data_type=weaviate.classes.config.DataType.TEXT,
                            description="Event magnitude/strength"
                        ),
                        weaviate.classes.config.Property(
                            name="magnitude_scale",
                            data_type=weaviate.classes.config.DataType.TEXT,
                            description="Scale used for magnitude (e.g., Kph, Richter)"
                        ),
                        weaviate.classes.config.Property(
                            name="description",
                            data_type=weaviate.classes.config.DataType.TEXT,
                            description="Generated description of the event"
                        )
                    ],
                    vectorizer_config=weaviate.classes.config.Configure.Vectorizer.text2vec_openai(),
                    generative_config=weaviate.classes.config.Configure.Generative.openai()
                )
                logger.info("HistoricalWeatherEvent collection created successfully")
            except Exception as create_error:
                logger.warning(
                    f"Cannot create HistoricalWeatherEvent collection (likely permissions issue): "
                    f"{create_error}"
                )
                logger.info(
                    "HistoricalWeatherEvent collection will need to be created "
                    "manually in Weaviate dashboard"
                )
        except Exception as e:
            logger.error(f"Error setting up HistoricalWeatherEvent schema: {e}")

    def search_historical_events(self, 
                                query: str, 
                                limit: int = 10,
                                event_type: Optional[str] = None,
                                country: Optional[str] = None,
                                min_fatalities: Optional[int] = None,
                                start_year: Optional[int] = None,
                                end_year: Optional[int] = None) -> List[Dict[str, Any]]:
        """Search historical events using vector similarity and filters."""
        if not self.client:
            return []

        try:
            collection = self.client.collections.get("HistoricalWeatherEvent")
            
            # Build where clause for filters
            where_clause = None
            if event_type or country or min_fatalities or start_year or end_year:
                conditions = []
                
                if event_type:
                    conditions.append({
                        "path": ["event_type"],
                        "operator": "Equal",
                        "valueText": event_type
                    })
                
                if country:
                    conditions.append({
                        "path": ["country"],
                        "operator": "Equal", 
                        "valueText": country
                    })
                
                if min_fatalities:
                    conditions.append({
                        "path": ["fatalities"],
                        "operator": "GreaterThanEqual",
                        "valueNumber": min_fatalities
                    })
                
                if start_year:
                    conditions.append({
                        "path": ["start_date"],
                        "operator": "GreaterThanEqual",
                        "valueDate": f"{start_year}-01-01T00:00:00Z"
                    })
                
                if end_year:
                    conditions.append({
                        "path": ["start_date"],
                        "operator": "LessThanEqual",
                        "valueDate": f"{end_year}-12-31T23:59:59Z"
                    })
                
                if len(conditions) == 1:
                    where_clause = conditions[0]
                elif len(conditions) > 1:
                    where_clause = {
                        "operator": "And",
                        "operands": conditions
                    }

            # Perform BM25 search
            if where_clause:
                results = collection.query.bm25(
                    query=query,
                    limit=limit,
                    where=where_clause
                )
            else:
                results = collection.query.bm25(
                    query=query,
                    limit=limit
                )

            # Convert results to list of dictionaries
            events = []
            for result in results.objects:
                event = {
                    'event_id': result.properties.get('event_id', ''),
                    'event_name': result.properties.get('event_name', ''),
                    'country': result.properties.get('country', ''),
                    'location': result.properties.get('location', ''),
                    'event_type': result.properties.get('event_type', ''),
                    'event_subtype': result.properties.get('event_subtype', ''),
                    'start_date': result.properties.get('start_date', ''),
                    'end_date': result.properties.get('end_date', ''),
                    'fatalities': result.properties.get('fatalities', 0),
                    'affected': result.properties.get('affected', 0),
                    'damage_usd': result.properties.get('damage_usd', 0),
                    'latitude': result.properties.get('latitude'),
                    'longitude': result.properties.get('longitude'),
                    'magnitude': result.properties.get('magnitude', ''),
                    'magnitude_scale': result.properties.get('magnitude_scale', ''),
                    'description': result.properties.get('description', ''),
                    'similarity_score': result.metadata.distance if result.metadata else None
                }
                events.append(event)

            return events

        except Exception as e:
            logger.error(f"Error searching historical events: {e}")
            return []


    def get_event_statistics(self) -> Dict[str, Any]:
        """Get statistics about the historical events in the database."""
        if not self.client:
            return {}

        try:
            collection = self.client.collections.get("HistoricalWeatherEvent")
            
            # Get total count
            total_count = collection.aggregate.over_all(total_count=True).total_count
            
            # Get event type distribution using simple query
            event_type_distribution = {}
            country_distribution = {}
            
            # Sample events to get distribution
            result = collection.query.fetch_objects(limit=1000)
            if result and hasattr(result, 'objects'):
                for obj in result.objects:
                    event_type = obj.properties.get('event_type', 'Unknown')
                    country = obj.properties.get('country', 'Unknown')
                    
                    event_type_distribution[event_type] = event_type_distribution.get(event_type, 0) + 1
                    country_distribution[country] = country_distribution.get(country, 0) + 1
            
            # Get top 10 countries
            top_countries = dict(sorted(country_distribution.items(), key=lambda x: x[1], reverse=True)[:10])
            
            return {
                'total_events': total_count,
                'event_types': event_type_distribution,
                'top_countries': top_countries
            }

        except Exception as e:
            logger.error(f"Error getting event statistics: {e}")
            return {}
