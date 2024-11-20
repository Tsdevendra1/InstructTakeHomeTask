from collections.abc import Generator
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from openai.types.chat import ChatCompletionMessage
from openai.types.chat.chat_completion import ChatCompletion, Choice

from scraping.services.openai_service import get_ai_response


class TestGetAIResponse:
    @pytest.fixture
    def mock_openai_response(self) -> ChatCompletion:
        mock_message = ChatCompletionMessage(
            content="This is a test answer",
            role="assistant",
            function_call=None,
            tool_calls=None,
        )

        mock_choice = Choice(
            finish_reason="stop",
            index=0,
            message=mock_message,
        )

        return ChatCompletion(
            id="test-id",
            model="gpt-4-mini",
            object="chat.completion",
            created=1234567890,
            choices=[mock_choice],
        )

    @pytest.fixture
    def mock_openai_client(self) -> Generator[Mock, None, None]:
        with patch("scraping.services.openai_service.OpenAI") as mock_client:
            instance = mock_client.return_value
            yield instance

    def test_valid_input__returns_expected_response(
        self, mock_openai_client: Mock, mock_openai_response: ChatCompletion
    ) -> None:
        mock_openai_client.chat.completions.create.return_value = mock_openai_response
        test_content = "Test Wikipedia content"
        test_question = "Test question?"

        response = get_ai_response(test_content, test_question)

        assert response.answer == "This is a test answer"

        mock_openai_client.chat.completions.create.assert_called_once_with(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on provided Wikipedia content. Only use the provided content to answer questions.",
                },
                {
                    "role": "user",
                    "content": "Based on the following Wikipedia content, please answer the question.\n        Answer directly and concisely. If the answer cannot be found in the content, say so.\n\n        Content:\n        Test Wikipedia content\n\n        Question: Test question?",
                },
            ],
        )

    @pytest.mark.parametrize("return_value", ["", None])
    def test_openai_returns_empty_content__returns_no_answer(
        self, mock_openai_client: Mock, mock_openai_response: ChatCompletion, return_value: str | None
    ) -> None:
        mock_openai_response.choices[0].message.content = return_value
        mock_openai_client.chat.completions.create.return_value = mock_openai_response
        test_content = "Test Wikipedia content"
        test_question = "Test question?"

        response = get_ai_response(test_content, test_question)

        assert response.answer == "No answer found in content"

    def test_empty_content__raises_error(self, mock_openai_client: Mock) -> None:
        test_content = ""
        test_question = "Test question?"

        with pytest.raises(HTTPException):
            get_ai_response(test_content, test_question)

        mock_openai_client.chat.completions.create.assert_not_called()

    def test_empty_question__does_not_call_api(self, mock_openai_client: Mock) -> None:
        test_content = "Test Wikipedia content"
        test_question = ""

        with pytest.raises(HTTPException):
            get_ai_response(test_content, test_question)

        mock_openai_client.chat.completions.create.assert_not_called()

    def test_api_error__raises_http_exception(self, mock_openai_client: Mock) -> None:
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")

        with pytest.raises(HTTPException) as exc_info:
            get_ai_response("Test content", "Test question")
