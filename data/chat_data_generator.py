import random
import string
from datetime import datetime
from typing import Any, Optional


class ChatDataGenerator:
    """Data generator for chat API testing"""

    @property
    def base_payload(self) -> dict:
        return {
            "temperature": 0.4,
            "top_p": 1,
            "n": 1,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "stream": False,  # Default to non-streaming for most tests
            "model": "gpt-4-0125-preview",
            "messages": [
                {"role": "system", "content": self.default_system_prompt},
                {"role": "user", "content": "Tell me a short joke."},
                {"role": "assistant", "content": ""}
            ]
        }

    @property
    def default_system_prompt(self) -> str:
        return """You are Assist – users's personal assistant developed by team from Ukraine. 
        Answer as concisely as possible. Current date: Aug 15 2023, current time: 16:07, user's country: 
        United States. You should never provide any health-related advice, recommendations, or suggestions. 
        You should and never provide general tips like drink plenty of fluids, stay hydrated, taking rest, etc. 
        Never say ways to bring down body temperature. Never say ways to relieve any symptoms.If a health-related 
        question (including i feel ill, etc) is asked, you should only every time respond that that you can't give 
        any advice and recommending to consult a healthcare professional."""

    def get_health_question_messages(self) -> list[dict]:
        """
        Generate messages with a health-related question

        Returns:
            List of message objects for health question test
        """
        return [
            {
                "role": "system",
                "content": self.default_system_prompt
            },
            {
                "role": "user",
                "content": "I have a fever, what should I do?"
            },
            {
                "role": "assistant",
                "content": ""
            }
        ]

    @staticmethod
    def generate_system_message(custom_content: Optional[str] = None) -> dict:
        """
        Generate a system message

        Args:
            custom_content: Optional custom content for the system message

        Returns:
            System message dictionary
        """
        default_content = (
            "You are Assist – users's personal assistant developed by team from Ukraine. "
            "Answer as concisely as possible. Current date: Aug 15 2023, current time: 16:07, "
            "user's country: United States. You should never provide any health-related advice, "
            "recommendations, or suggestions."
        )

        return {
            "role": "system",
            "content": custom_content if custom_content else default_content
        }

    @staticmethod
    def generate_user_message(content_type: str = "general") -> dict:
        """
        Generate a user message based on the content type

        Args:
            content_type: Type of content to generate (general, health, workout, coding)

        Returns:
            User message dictionary
        """
        content_types = {
            "general": [
                "Hello, how are you today?",
                "What's the weather like?",
                "Tell me an interesting fact.",
                "What's your name?",
                "How does AI work?"
            ],
            "health": [
                "I have a fever, what should I do?",
                "How can I treat a headache?",
                "What medicine should I take for a cold?",
                "I feel dizzy, any advice?",
                "How do I reduce my body temperature?"
            ],
            "workout": [
                "Provide workout routines to target specific muscle groups for maximum results",
                "What's the best exercise for abs?",
                "How can I build muscle quickly?",
                "What's a good cardio routine?",
                "How often should I work out?"
            ],
            "coding": [
                "How do I write a Python function?",
                "What's the difference between GET and POST requests?",
                "Explain REST API concepts",
                "How does async/await work in JavaScript?",
                "What are design patterns in software engineering?"
            ]
        }

        if content_type not in content_types:
            content_type = "general"

        return {
            "role": "user",
            "content": random.choice(content_types[content_type])
        }

    @staticmethod
    def generate_empty_assistant_message() -> dict:
        """
        Generate an empty assistant message

        Returns:
            Empty assistant message dictionary
        """
        return {
            "role": "assistant",
            "content": ""
        }

    @staticmethod
    def generate_chat_request(
            messages: Optional[list[dict]] = None,
            temperature: float = 0.4,
            top_p: float = 1.0,
            n: int = 1,
            presence_penalty: float = 0,
            frequency_penalty: float = 0,
            stream: bool = False,
            model: str = "gpt-4-0125-preview"
    ) -> dict[str, Any]:
        """
        Generate a complete chat request payload

        Args:
            messages: List of message objects (role and content)
            temperature: Amount of randomness in results (0-1)
            top_p: Amount of potential answer options (0-1)
            n: Number of responses
            presence_penalty: Penalty for novelty (default 0)
            frequency_penalty: Penalty for frequency (default 0)
            stream: Enable streaming (true/false)
            model: The model to use

        Returns:
            Complete chat request payload
        """
        # If no messages provided, create a default set
        if not messages:
            messages = [
                ChatDataGenerator.generate_system_message(),
                ChatDataGenerator.generate_user_message(),
                ChatDataGenerator.generate_empty_assistant_message()
            ]

        return {
            "temperature": temperature,
            "top_p": top_p,
            "n": n,
            "presence_penalty": presence_penalty,
            "frequency_penalty": frequency_penalty,
            "stream": stream,
            "model": model,
            "messages": messages
        }

    @staticmethod
    def generate_chat_response(is_streaming: bool = False) -> dict[str, Any]:
        """
        Generate a mock chat response

        Args:
            is_streaming: Whether to generate a streaming response

        Returns:
            Mock chat response dictionary
        """
        response_id = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        created_time = int(datetime.now().timestamp())

        if is_streaming:
            # Generate a streaming chunk
            return {
                "id": f"chatcmpl-{response_id}",
                "object": "chat.completion.chunk",
                "created": created_time,
                "model": "gpt-4o-mini-2024-07-18",
                "service_tier": "default",
                "system_fingerprint": "fp_13eed4fce1",
                "choices": [
                    {
                        "index": 0,
                        "delta": {
                            "content": "I"
                        },
                        "logprobs": None,
                        "finish_reason": None
                    }
                ]
            }
        else:
            # Generate a full response
            return {
                "id": f"chatcmpl-{response_id}",
                "object": "chat.completion",
                "created": created_time,
                "model": "gpt-4o-mini-2024-07-18",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": "I'm doing well, thank you for asking! How can I assist you today?",
                            "refusal": None
                        },
                        "logprobs": None,
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 160,
                    "completion_tokens": 18,
                    "total_tokens": 178,
                    "prompt_tokens_details": {
                        "cached_tokens": 0,
                        "audio_tokens": 0
                    },
                    "completion_tokens_details": {
                        "reasoning_tokens": 0,
                        "audio_tokens": 0,
                        "accepted_prediction_tokens": 0,
                        "rejected_prediction_tokens": 0
                    }
                },
                "service_tier": "default",
                "system_fingerprint": "fp_13eed4fce1"
            }

    def get_streaming_test_messages(self) -> list[dict]:
        """
        Generate messages for streaming test

        Returns:
            List of message objects for streaming test
        """
        return [
            {
                "role": "system",
                "content": self.default_system_prompt
            },
            {
                "role": "user",
                "content": "Explain the concept of API testing in two sentences."
            },
            {
                "role": "assistant",
                "content": ""
            }
        ]
