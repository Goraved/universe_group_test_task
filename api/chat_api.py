import json

import httpx

from api.base_api import BaseApi


class ChatApi(BaseApi):
    """Class for working with Chat API"""

    def __init__(self, base_url: str, token: str):
        """
        Initialize the ChatApi object

        Args:
            base_url: Base URL for the API
            token: JWT token for authorization
        """
        super().__init__(base_url=base_url, token=token)
        self.default_headers = self.headers

    def post_chat_completion(self,
                             messages: list[dict],
                             model: str = "gpt-4-0125-preview",
                             temperature: float = 0.4,
                             top_p: float = 1.0,
                             n: int = 1,
                             presence_penalty: float = 0,
                             frequency_penalty: float = 0,
                             stream: bool = False,
                             expected_status: int = 200) -> httpx.Response:
        """
        Send a request to the chat completions endpoint

        Args:
            messages: List of message objects (role and content)
            model: The model to use
            temperature: Amount of randomness in results (0-1)
            top_p: Amount of potential answer options (0-1)
            n: Number of responses
            presence_penalty: Penalty for novelty (default 0)
            frequency_penalty: Penalty for frequency (default 0)
            stream: Enable streaming (true/false)
            expected_status: Expected HTTP status code

        Returns:
            Server response
        """
        endpoint = "/stream/v1/chat/completions"

        data = {
            "temperature": temperature,
            "top_p": top_p,
            "n": n,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "stream": stream,
            "model": model,
            "messages": messages
        }

        return self.post(endpoint, data=data, expected_status=expected_status)

    @staticmethod
    def parse_stream_data(response: httpx.Response) -> list[dict]:
        """
        Parse streaming response data

        Args:
            response: Server response with streaming data

        Returns:
            List of parsed chunks
        """
        chunks = []

        # Read and parse each chunk
        for line in response.iter_lines():
            # Check if line exists and decode it first
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    # Remove 'data: ' prefix
                    json_str = line_str[6:]
                    # Skip 'data: [DONE]' message that may appear at the end
                    if json_str != '[DONE]':
                        try:
                            chunk = json.loads(json_str)
                            chunks.append(chunk)
                        except json.JSONDecodeError:
                            pass  # Skip invalid JSON chunks

        return chunks
