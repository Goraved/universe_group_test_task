from json import JSONDecodeError
from typing import Union, Optional

import httpx


class BaseApi:
    """Base class for API operations"""

    def __init__(self, base_url: str, token: str = None):
        """
        Initialize the BaseApi object

        Args:
            base_url: Base URL for the API
            token: JWT token for authorization
        """
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
            'Accept-Encoding': 'gzip, deflate, br'
        }

        # Add token if provided
        if token:
            self.headers['Authorization'] = f'Bearer {token}'

        # Configure HTTP client
        self.client = httpx.Client(
            headers=self.headers,
            timeout=30,  # 30 seconds timeout
            http2=True  # Use HTTP/2
        )

    def __del__(self):
        """Ensure the HTTP client is properly closed"""
        if hasattr(self, 'client'):
            self.client.close()

    def request(self, method: str, url: str, headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """
        Generic request method

        Args:
            method: HTTP method (GET, POST, etc.)
            url: API endpoint
            headers: Additional headers
            **kwargs: Extra arguments like data, params, etc.

        Returns:
            The server response
        """
        full_url = f'{self.base_url}{url}'
        request_headers = headers or self.headers
        expected_status = kwargs.pop('expected_status', None)

        # Convert data to JSON for POST/PUT requests
        if method in ('POST', 'PUT', 'PATCH') and 'data' in kwargs:
            data = kwargs['data']
            if isinstance(data, (dict, list)) and not isinstance(data, str):
                kwargs['json'] = data
                kwargs.pop('data')

        # Make the request
        response = self.client.request(method, full_url, headers=request_headers, **kwargs)

        # Validate response status
        if expected_status:
            self.check_status_code(response, expected_status)

        return response

    def get(self, url: str, headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """Send a GET request"""
        return self.request('GET', url, headers, **kwargs)

    def post(self, url: str, data: Union[list, dict, str], headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """Send a POST request"""
        return self.request('POST', url, headers=headers, data=data, **kwargs)

    def put(self, url: str, data: Union[list, dict, str], headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """Send a PUT request"""
        return self.request('PUT', url, headers=headers, data=data, **kwargs)

    def patch(self, url: str, data: Union[list, dict, str], headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """Send a PATCH request"""
        return self.request('PATCH', url, headers=headers, data=data, **kwargs)

    def delete(self, url: str, headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """Send a DELETE request"""
        return self.request('DELETE', url, headers, **kwargs)

    def head(self, url: str, headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """Send a HEAD request"""
        return self.request('HEAD', url, headers, **kwargs)

    def options(self, url: str, headers: Optional[dict] = None, **kwargs) -> httpx.Response:
        """Send an OPTIONS request"""
        return self.request('OPTIONS', url, headers, **kwargs)

    @staticmethod
    def check_status_code_success(response: httpx.Response) -> None:
        """
        Ensure response status is in the 2xx range.

        Args:
            response (httpx.Response): The server response.

        Raises:
            AssertionError: If the response status code is not in the 2xx range.
        """
        assert str(response.status_code).startswith('2'), \
            f'Response code = {response.status_code}, error = {response.reason_phrase} {response.text}'

    @staticmethod
    def check_status_code(response: httpx.Response, expected_code: int) -> None:
        """
        Ensure response status matches the expected code.

        Args:
            response (httpx.Response): The server response.
            expected_code (int): The expected HTTP status code.

        Raises:
            AssertionError: If the response status code does not match the expected code.
        """
        if response.status_code == 200:
            error = None
        else:
            try:
                error = BaseApi.parse_response_to_json(response)
            except JSONDecodeError:
                error = 'Unable to parse error'

        assert response.status_code == expected_code, \
            f'Wrong response code. Expected = {expected_code}, received = {response.status_code} | error = {error}'

    @staticmethod
    def parse_response_to_json(response: httpx.Response) -> Union[list, dict]:
        """
        Parse response content to JSON

        Args:
            response: The server response

        Returns:
            Parsed JSON content
        """
        return response.json()
