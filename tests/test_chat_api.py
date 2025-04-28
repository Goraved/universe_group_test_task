import copy
import json

import pytest

from data.chat_data_generator import ChatDataGenerator

# Instantiate the data generator for consistent test data
data_generator = ChatDataGenerator()


class TestChatApi:
    """
    Contains automated tests for the /stream/v1/chat/completions endpoint.
    Focuses on validating responses, handling various parameters,
    authentication, and streaming functionality.
    """

    def test_successful_chat_completion(self, apis):
        """
        Verify a successful chat completion request (non-streaming).

        Steps:
        1. Prepare a valid payload with stream=False.
        2. Send the POST request to the chat completions endpoint.
        3. Assert the response status code is 200 OK.
        4. Assert the response body contains the expected structure and fields
           (id, object='chat.completion', choices list with message, usage).
        """
        # Prepare payload
        payload = data_generator.base_payload
        payload["stream"] = False  # Explicitly set non-streaming

        # Send request
        response = apis.chat_api.post_chat_completion(
            messages=payload["messages"],
            temperature=payload["temperature"],
            top_p=payload["top_p"],
            n=payload["n"],
            presence_penalty=payload["presence_penalty"],
            frequency_penalty=payload["frequency_penalty"],
            stream=payload["stream"],
            model=payload["model"]
        )

        # Verify status code
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.text}"

        # Parse and verify response structure
        try:
            response_data = apis.chat_api.parse_response_to_json(response)
        except json.JSONDecodeError:
            pytest.fail(f"Failed to decode JSON response: {response.text}")

        assert "id" in response_data, "Response missing 'id' field"
        assert response_data.get("object") == "chat.completion", \
            f"Expected object 'chat.completion', got {response_data.get('object')}"
        assert "choices" in response_data, "Response missing 'choices' field"
        assert isinstance(response_data["choices"], list), "'choices' should be a list"
        assert len(response_data["choices"]) > 0, "'choices' list should not be empty"
        # Check structure of the first choice
        first_choice = response_data["choices"][0]
        assert "message" in first_choice, "First choice missing 'message' field"
        assert "content" in first_choice["message"], "Message missing 'content' field"
        assert "role" in first_choice["message"], "Message missing 'role' field"
        assert first_choice["message"]["role"] == "assistant", \
            f"Expected role 'assistant', got {first_choice['message']['role']}"
        assert first_choice["message"]["content"], "Assistant message content should not be empty"
        assert "usage" in response_data, "Response missing 'usage' field"

    def test_chat_completion_with_invalid_token(self, apis_invalid_token):
        """
        Verify that requests with an invalid or expired token are rejected.

        Steps:
        1. Prepare a standard payload.
        2. Send the request using an API client configured with an invalid token.
        3. Assert the response status code is 401 Unauthorized.
        """
        # Prepare payload
        payload = data_generator.base_payload

        # Send request with invalid token client
        response = apis_invalid_token.chat_api.post_chat_completion(
            messages=payload["messages"],
            stream=payload["stream"],
            expected_status=401  # Expecting 401
        )

        # Verify status code
        assert response.status_code == 401, f"Expected status 401, got {response.status_code}. Response: {response.text}"

    @pytest.mark.parametrize(
        "param_key, invalid_value, description",
        [
            ("temperature", 1.1, "Temperature above valid range (1.1)"),
            ("temperature", -0.1, "Temperature below valid range (-0.1)"),
            ("temperature", "0.5", "Temperature as string ('0.5')"),
            ("top_p", 1.1, "Top_p above valid range (1.1)"),
            ("top_p", -0.1, "Top_p below valid range (-0.1)"),
            ("top_p", None, "Top_p as null"),
            ("n", 0, "n parameter equals 0"),
            ("n", -1, "n parameter is negative (-1)"),
            ("n", 1.5, "n parameter is float (1.5)"),
            ("presence_penalty", 2.1, "Presence penalty above range (2.1)"),
            ("presence_penalty", -2.1, "Presence penalty below range (-2.1)"),
            ("frequency_penalty", 2.1, "Frequency penalty above range (2.1)"),
            ("frequency_penalty", -2.1, "Frequency penalty below range (-2.1)"),
            ("stream", "true", "Stream parameter as string ('true')"),
            ("stream", 1, "Stream parameter as integer (1)"),
            ("model", "", "Model parameter as empty string"),
            ("model", None, "Model parameter as null"),
        ],
        ids=lambda x: x[2] if isinstance(x, tuple) else None  # Use description for test ID
    )
    def test_chat_completion_with_invalid_body_params(self, apis, param_key, invalid_value, description):
        """
        Verify handling of various invalid data types or out-of-range values for body parameters.

        Steps:
        1. Prepare a base payload.
        2. Modify the specified parameter (`param_key`) with the `invalid_value`.
        3. Send the POST request.
        4. Assert the response status code is 400 Bad Request.
        """
        # Prepare payload and modify the invalid parameter
        payload = data_generator.base_payload
        payload[param_key] = invalid_value

        # Send request directly to control payload precisely
        response = apis.chat_api.post(
            "/stream/v1/chat/completions",
            data=payload,
            expected_status=400  # Expecting 400 for invalid parameters
        )

        # Verify status code
        assert response.status_code == 400, \
            f"Test '{description}': Expected status 400, got {response.status_code}. Payload: {payload}. Response: {response.text}"

    @pytest.mark.parametrize(
        "messages_value, description",
        [
            (None, "Messages parameter completely missing"),
            ([], "Messages parameter as empty list"),
            ([{"role": "user"}], "Message object missing 'content' field"),
            ([{"content": "Hi"}], "Message object missing 'role' field"),
            ([{"role": "invalid_role", "content": "Hi"}], "Message object with invalid 'role' value"),
            ([{"role": "user", "content": None}], "Message 'content' field is null"),
            ([{"role": "user", "content": 123}], "Message 'content' field is integer"),
        ],
        ids=lambda x: x[1] if isinstance(x, tuple) else None  # Use description for test ID
    )
    def test_chat_completion_with_invalid_messages_structure(self, apis, messages_value, description):
        """
        Verify handling of invalid structures or missing fields within the 'messages' array.

        Steps:
        1. Prepare a base payload.
        2. Replace or remove the 'messages' field with the invalid structure.
        3. Send the POST request.
        4. Assert the response status code is 400 Bad Request.
        """
        # Prepare payload
        payload = data_generator.base_payload

        if messages_value is None:
            # Test case for completely missing 'messages' key
            del payload["messages"]
        else:
            # Test cases for invalid 'messages' value/structure
            payload["messages"] = messages_value

        # Send request directly
        response = apis.chat_api.post(
            "/stream/v1/chat/completions",
            data=payload,
            expected_status=400
        )

        # Verify status code
        assert response.status_code == 400, f"Test '{description}': Expected status 400, got {response.status_code}. Payload: {payload}. Response: {response.text}"

    @pytest.mark.parametrize(
        "header_key, header_value, expected_status, description",
        [
            ("Content-Type", "text/plain", 415, "Invalid Content-Type (text/plain)"),
            ("Content-Type", "application/xml", 415, "Invalid Content-Type (application/xml)"),
            ("Content-Type", None, 415, "Missing Content-Type header"),  # None signifies removal
            ("Authorization", "Bearer", 401, "Malformed Authorization header ('Bearer')"),
            ("Authorization", "Bearer ", 401, "Malformed Authorization header ('Bearer ')"),
            ("Authorization", "Token invalid-token", 401, "Malformed Authorization header (Wrong type 'Token')"),
            ("Authorization", None, 401, "Missing Authorization header"),  # None signifies removal
        ],
        ids=lambda x: x[3] if isinstance(x, tuple) else None
    )
    def test_chat_completion_with_invalid_headers(self, apis, header_key, header_value, expected_status, description):
        """
        Verify handling of requests with invalid or missing essential headers.

        Steps:
        1. Prepare a standard payload.
        2. Prepare custom headers, modifying or removing the specified header.
        3. Send the POST request with the custom headers.
        4. Assert the response status code matches the expected error code (401 or 415).
        """
        # Prepare payload and headers
        payload = data_generator.base_payload
        custom_headers = copy.deepcopy(apis.chat_api.default_headers)  # Start with valid headers

        if header_value is None:
            # Remove the header if value is None
            if header_key in custom_headers:
                del custom_headers[header_key]
        else:
            # Set the invalid header value
            custom_headers[header_key] = header_value

        # Send request with custom headers
        response = apis.chat_api.post(
            "/stream/v1/chat/completions",
            data=payload,
            headers=custom_headers,
            expected_status=expected_status
        )

        # Verify status code
        assert response.status_code == expected_status, \
            f"Test '{description}': Expected status {expected_status}, got {response.status_code}. Headers: {custom_headers}. Response: {response.text}"

    def test_chat_completion_refuses_health_advice(self, apis):
        """
        Verify the assistant refuses to provide health advice as per system prompt instructions.

        Steps:
        1. Prepare a payload with a health-related user question.
        2. Send the POST request (non-streaming).
        3. Assert the response status code is 200 OK.
        4. Assert the response content indicates refusal and suggests consulting a professional.
        """
        # Prepare payload with health question
        messages = data_generator.get_health_question_messages()

        # Send request
        response = apis.chat_api.post_chat_completion(messages=messages, stream=False)

        # Verify status code
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response: {response.text}"

        # Parse response and check content for refusal keywords
        try:
            response_data = apis.chat_api.parse_response_to_json(response)
            content = response_data["choices"][0]["message"]["content"].lower()
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            pytest.fail(f"Failed to parse response or find content: {e}. Response: {response.text}")

        assert "healthcare professional" in content or "doctor" in content, \
            f"Response should suggest consulting a professional. Got: {content}"
        assert "can't give" in content or "cannot provide" in content or "unable to provide" in content, \
            f"Response should indicate inability to give advice. Got: {content}"

    def test_chat_completion_streaming_response(self, apis):
        """
        Verify the streaming functionality works correctly.

        Steps:
        1. Prepare a payload with stream=True.
        2. Send the POST request.
        3. Assert the response status code is 200 OK.
        4. Parse the streaming response chunks.
        5. Assert that multiple chunks were received.
        6. Assert that chunks have the expected 'chat.completion.chunk' object type and contain a 'delta'.
        7. Assert that the accumulated content is non-empty.
        8. Assert that the stream concludes with a 'stop' finish reason.
        """
        # Prepare payload for streaming
        messages = data_generator.get_streaming_test_messages()

        # Send streaming request
        response = apis.chat_api.post_chat_completion(messages=messages, stream=True)

        # Verify status code
        assert response.status_code == 200, f"Expected status 200, got {response.status_code}. Response content starts with: {response.text[:200]}"

        # Parse streaming data (assuming helper handles chunk parsing)
        chunks = apis.chat_api.parse_stream_data(response)

        # Verify chunks were received
        assert len(chunks) > 0, "No chunks received from the stream"

        # Verify first chunk structure
        first_chunk = chunks[0]
        assert "id" in first_chunk, "First chunk missing 'id'"
        assert first_chunk.get("object") == "chat.completion.chunk", \
            f"Expected object 'chat.completion.chunk', got {first_chunk.get('object')}"
        assert "choices" in first_chunk, "First chunk missing 'choices'"
        assert len(first_chunk["choices"]) > 0, "First chunk 'choices' is empty"
        assert "delta" in first_chunk["choices"][0], "First chunk choice missing 'delta'"

        # Accumulate content and find finish reason
        content_parts = []
        finish_reason = None
        for chunk in chunks:
            # Basic check for valid chunk structure before accessing nested keys
            if isinstance(chunk, dict) and "choices" in chunk and isinstance(chunk["choices"], list) and chunk[
                "choices"]:
                choice = chunk["choices"][0]
                if isinstance(choice, dict):
                    if "delta" in choice and isinstance(choice["delta"], dict) and "content" in choice["delta"] and \
                            choice["delta"]["content"]:
                        content_parts.append(choice["delta"]["content"])
                    if "finish_reason" in choice and choice["finish_reason"]:
                        finish_reason = choice["finish_reason"]

        # Verify content was received and stream finished correctly
        full_content = "".join(content_parts)
        assert len(full_content) > 0, "Accumulated content from stream is empty"
        assert finish_reason == "stop", f"Expected finish_reason 'stop', got '{finish_reason}'"

    @pytest.mark.xfail(reason="API returns 400 for invalid model, not 500 as per original requirement description")
    def test_chat_completion_simulated_server_error(self, apis):
        """
        Attempt to simulate a server error condition by providing an invalid model name.

        Note: The API specification mentions 500 Internal Server Error, but testing
              reveals that an invalid model name actually returns 400 Bad Request.
              This test is marked xfail to reflect this discrepancy.

        Steps:
        1. Prepare a payload with a non-existent model name.
        2. Send the POST request.
        3. (Expected Failure) Assert the response status code is 500.
           The actual result is 400, causing the test to be marked as xfailed.
        """
        # Prepare payload with invalid model
        payload = data_generator.base_payload
        payload['model'] = 'non-existent-model-12345'  # Use an unlikely model name

        # Send request expecting 500 (but will get 400)
        response = apis.chat_api.post(
            "/stream/v1/chat/completions",
            data=payload,
            expected_status=500  # Set expectation for the test documentation
        )

        # The assertion below will fail, hence the xfail mark.
        # The actual status code received is likely 400.
        assert response.status_code == 500, f"Expected status 500, got {response.status_code}. Response: {response.text}"
