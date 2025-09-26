import requests
import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class PexelsService:
    """Service for fetching weather-related images from Pexels API."""
    
    def __init__(self):
        self.api_key = os.getenv("PEXELS_API_KEY")
        self.base_url = "https://api.pexels.com/v1"
        self.headers = {
            "Authorization": self.api_key
        } if self.api_key else {}
    
    def get_weather_image(self, condition: str, city: str = None) -> Optional[Dict[str, Any]]:
        """
        Get a weather-related image from Pexels.
        
        Args:
            condition: Weather condition (e.g., 'rain', 'sunny', 'snow')
            city: Optional city name for location-specific images
            
        Returns:
            Dict with image data or None if not found
        """
        if not self.api_key:
            logger.warning("PEXELS_API_KEY not found in environment variables")
            return None
        
        try:
            # Build search query
            search_terms = self._build_search_query(condition, city)
            
            # Try different search terms until we find an image
            for query in search_terms:
                image_data = self._search_images(query)
                if image_data:
                    return image_data
            
            logger.warning(f"No images found for weather condition: {condition}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching weather image: {str(e)}")
            return None
    
    def _build_search_query(self, condition: str, city: str = None) -> list:
        """Build search queries with different combinations."""
        queries = []
        
        # Clean up condition for better search results
        condition_clean = condition.lower().strip()
        
        # Map weather conditions to better search terms
        condition_mapping = {
            'rain': ['rain weather', 'rainy day', 'rain storm', 'rain drops', 'rainy street'],
            'light rain': ['light rain', 'drizzle', 'rain drops', 'gentle rain'],
            'moderate rain': ['moderate rain', 'rain weather', 'rainy day'],
            'heavy rain': ['heavy rain', 'rain storm', 'downpour', 'rain storm'],
            'snow': ['snow weather', 'snowy day', 'winter snow', 'snow landscape'],
            'light snow': ['light snow', 'snowflakes', 'gentle snow'],
            'clear sky': ['clear sky', 'blue sky', 'sunny weather', 'clear day'],
            'sunny': ['sunny weather', 'clear sky', 'sunny day', 'bright day'],
            'few clouds': ['few clouds', 'partly cloudy', 'clouds sky', 'mixed weather'],
            'scattered clouds': ['scattered clouds', 'cloudy sky', 'clouds weather'],
            'broken clouds': ['broken clouds', 'cloudy weather', 'clouds sky'],
            'overcast clouds': ['overcast clouds', 'cloudy weather', 'cloudy day'],
            'cloudy': ['cloudy weather', 'clouds', 'overcast', 'cloudy day'],
            'storm': ['storm weather', 'thunderstorm', 'storm clouds', 'stormy weather'],
            'thunderstorm': ['thunderstorm', 'storm weather', 'lightning storm'],
            'fog': ['fog weather', 'foggy day', 'mist', 'foggy landscape'],
            'mist': ['mist weather', 'foggy day', 'misty landscape'],
            'haze': ['haze weather', 'hazy day', 'atmospheric haze'],
            'wind': ['windy weather', 'wind storm', 'strong wind', 'windy day'],
            'clear': ['clear sky', 'blue sky', 'sunny weather', 'clear day'],
            'partly cloudy': ['partly cloudy', 'clouds sky', 'mixed weather', 'cloudy sky']
        }
        
        # Get specific terms for the condition
        if condition_clean in condition_mapping:
            base_terms = condition_mapping[condition_clean]
        else:
            base_terms = [f"{condition_clean} weather", condition_clean]
        
        # Add city-specific queries if provided
        if city:
            city_clean = city.lower().strip()
            for term in base_terms:
                queries.append(f"{term} {city_clean}")
                queries.append(f"{city_clean} {term}")  # Try both orders
        
        # Add general weather queries (lower priority)
        queries.extend(base_terms)
        
        # Add fallback queries for better results
        queries.extend([
            f"{condition_clean} sky",
            f"{condition_clean} landscape", 
            f"{condition_clean} nature",
            f"weather {condition_clean}",
            f"outdoor {condition_clean}"
        ])
        
        return queries
    
    def _search_images(self, query: str) -> Optional[Dict[str, Any]]:
        """Search for images with a specific query and validate relevance."""
        try:
            params = {
                "query": query,
                "per_page": 5,  # Get more results to filter
                "orientation": "landscape",
                "size": "medium"
            }
            
            response = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                photos = data.get("photos", [])
                
                if photos:
                    # Filter and validate images for weather relevance
                    for photo in photos:
                        if self._is_weather_relevant(photo, query):
                            return {
                                "url": photo["src"]["medium"],
                                "alt": photo["alt"],
                                "photographer": photo["photographer"],
                                "photographer_url": photo["photographer_url"],
                                "query": query
                            }
                    
                    # If no relevant images found, return the first one
                    photo = photos[0]
                    return {
                        "url": photo["src"]["medium"],
                        "alt": photo["alt"],
                        "photographer": photo["photographer"],
                        "photographer_url": photo["photographer_url"],
                        "query": query
                    }
            
            elif response.status_code == 429:
                logger.warning("Pexels API rate limit exceeded")
            else:
                logger.warning(f"Pexels API error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
        
        return None

    def _is_weather_relevant(self, photo: dict, query: str) -> bool:
        """Check if an image is relevant to weather conditions."""
        alt_text = photo.get("alt", "").lower()
        query_lower = query.lower()
        
        # Keywords that indicate weather relevance
        weather_keywords = [
            'weather', 'sky', 'cloud', 'rain', 'snow', 'sun', 'storm', 'fog', 'mist',
            'sunny', 'cloudy', 'rainy', 'snowy', 'stormy', 'foggy', 'clear', 'overcast',
            'lightning', 'thunder', 'drizzle', 'shower', 'breeze', 'wind', 'temperature',
            'climate', 'atmosphere', 'meteorology', 'forecast', 'outdoor', 'nature',
            'landscape', 'horizon', 'sunset', 'sunrise', 'daylight', 'dawn', 'dusk'
        ]
        
        # Keywords that indicate non-weather content (strong negative indicators)
        non_weather_keywords = [
            'house', 'building', 'construction', 'derelict', 'abandoned', 'ruin',
            'deteriorating', 'exposed', 'bricks', 'symbolizing', 'decay',
            'indoor', 'room', 'interior', 'furniture', 'car', 'vehicle', 'street',
            'city', 'urban', 'architecture', 'portrait', 'person', 'people', 'face',
            'food', 'restaurant', 'kitchen', 'office', 'work', 'business', 'shop',
            'store', 'market', 'product', 'object', 'tool', 'equipment', 'machine'
        ]
        
        # Check for weather relevance
        has_weather_keywords = any(keyword in alt_text for keyword in weather_keywords)
        has_non_weather_keywords = any(keyword in alt_text for keyword in non_weather_keywords)
        
        # Strong negative indicators - reject immediately
        strong_negative_indicators = ['deteriorating', 'derelict', 'abandoned', 'ruin', 'decay', 'exposed bricks']
        if any(indicator in alt_text for indicator in strong_negative_indicators):
            return False
        
        # If it has non-weather keywords and no weather keywords, it's not relevant
        if has_non_weather_keywords and not has_weather_keywords:
            return False
        
        # If it has weather keywords, it's likely relevant
        if has_weather_keywords:
            return True
        
        # For neutral content, check if query contains weather terms
        query_weather_terms = any(term in query_lower for term in ['weather', 'rain', 'snow', 'cloud', 'sun', 'storm'])
        if query_weather_terms:
            return True
        
        return False
    
    def get_fallback_image(self, condition: str) -> Optional[Dict[str, Any]]:
        """Get a fallback image for common weather conditions."""
        fallback_images = {
            'rain': {
                "url": "https://images.pexels.com/photos/39811/pexels-photo-39811.jpeg",
                "alt": "Rain weather",
                "photographer": "Pexels",
                "photographer_url": "https://www.pexels.com",
                "query": "rain fallback"
            },
            'snow': {
                "url": "https://images.pexels.com/photos/1261728/pexels-photo-1261728.jpeg",
                "alt": "Snow weather",
                "photographer": "Pexels",
                "photographer_url": "https://www.pexels.com",
                "query": "snow fallback"
            },
            'sunny': {
                "url": "https://images.pexels.com/photos/158827/field-corn-air-frisch-158827.jpeg",
                "alt": "Sunny weather",
                "photographer": "Pexels",
                "photographer_url": "https://www.pexels.com",
                "query": "sunny fallback"
            }
        }
        
        condition_clean = condition.lower().strip()
        return fallback_images.get(condition_clean)
