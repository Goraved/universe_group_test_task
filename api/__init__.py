import os
from functools import cached_property

from api.chat_api import ChatApi


class APIs:
    def __init__(self, token: str = None):
        """
        Initialize the APIs factory

        Args:
            token: JWT token for authorization (defaults to environment variable)
        """
        self.token = token if token else os.getenv('API_TOKEN',
                                                   'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwMTIxYjY4MC1hNmVmLTQzMGMtODhiZC02MTI5ZGY5MTc5YjMiLCJjcmVhdGVkX2F0IjoiMjAyNS0wMi0yOFQxNDowMTowOC4yODNaIiwiY3JlYXRlZEF0IjoiMjAyNS0wMi0yOFQxNDowMTowOC4yODNaIiwiaWF0IjoxNzQwNzUxMjY4LCJleHAiOjE3NDA3NTIxNjh9.nvgpPryJe9Y5jn5DP2D9YAU_yNZAV7pW913VgxusTyU')
        self.base_url = os.getenv('API_BASE_URL', 'https://automation-qa-test.universeapps.limited')

    @cached_property
    def chat_api(self) -> ChatApi:
        """
        Get or create a ChatApi instance

        Returns:
            Configured ChatApi instance
        """
        return ChatApi(self.base_url, self.token)

    def with_invalid_token(self) -> 'APIs':
        """
        Create a new APIs instance with an invalid token

        Returns:
            New APIs instance with invalid token
        """
        return APIs(token="invalid_token")
