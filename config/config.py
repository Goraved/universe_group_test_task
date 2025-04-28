import os
from dataclasses import dataclass


@dataclass
class ApiConfig:
    """API configuration data class"""
    base_url: str
    token: str


# Get values from environment variables or use defaults
BASE_URL = os.getenv('API_BASE_URL', 'https://automation-qa-test.universeapps.limited')
# Default token for testing (should be placed in the secret manager, or generated dynamically)
API_TOKEN = os.getenv('API_TOKEN')

# Invalid token for negative testing
INVALID_TOKEN = "invalid_token"

# Configuration object for API
api_config = ApiConfig(
    base_url=BASE_URL,
    token=API_TOKEN
)
