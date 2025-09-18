import pytest
import os

# Set test environment variables
os.environ["GOOGLE_API_KEY"] = "test_google_key"
os.environ["OPENWEATHER_API_KEY"] = "test_weather_key"


def test_environment_variables():
    """Test that environment variables are set."""
    assert os.getenv("GOOGLE_API_KEY") == "test_google_key"
    assert os.getenv("OPENWEATHER_API_KEY") == "test_weather_key"


if __name__ == "__main__":
    pytest.main([__file__])
