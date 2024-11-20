import base64

from fastapi import HTTPException
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from scraping.models import ScrapeAskQuestionResponse, ScrapingResponse


class TestPOST:
    endpoint = "/ask"

    def test_successful_request__returns_answer_to_question(
        self, client: TestClient, auth_headers: dict[str, str], mocker: MockerFixture
    ) -> None:
        mock_scrape_response = ScrapingResponse(
            title="Test Title",
            content="Test Content",
            image_url="https://example.com/image.jpg",
            categories=["test"],
            references=["test"],
        )
        mock_scrape = mocker.patch("scraping.router.webscrape_url", return_value=mock_scrape_response)
        mock_ai_response = ScrapeAskQuestionResponse(
            answer="This is the answer",
        )
        mock_ai = mocker.patch("scraping.router.get_ai_response", return_value=mock_ai_response)

        response = client.post(
            self.endpoint, json={"url": "https://example.com", "question": "What is this about?"}, headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json() == {
            "answer": mock_ai_response.answer,
        }

        mock_scrape.assert_called_once_with("https://example.com")
        mock_ai.assert_called_once_with("Test Content", "What is this about?")

    def test_ask_endpoint_failed_scraping__returns_error(
        self, client: TestClient, auth_headers: dict[str, str], mocker: MockerFixture
    ) -> None:
        mocker.patch(
            "scraping.router.webscrape_url",
            side_effect=HTTPException(status_code=500, detail="Failed to scrape website"),
        )

        response = client.post(
            self.endpoint, json={"url": "https://example.com", "question": "What is this about?"}, headers=auth_headers
        )

        assert response.json() == {"detail": "Failed to scrape website"}
        assert response.status_code == 500

    def test_ask_endpoint_failed_ai_response__returns_error(
        self, client: TestClient, auth_headers: dict[str, str], mocker: MockerFixture
    ) -> None:
        mock_scrape_response = ScrapingResponse(
            title="Test Title",
            content="Test Content",
            image_url="https://example.com/image.jpg",
            categories=["test"],
            references=["test"],
        )
        mocker.patch("scraping.router.webscrape_url", return_value=mock_scrape_response)

        mocker.patch(
            "scraping.router.get_ai_response",
            side_effect=HTTPException(status_code=500, detail="Failed to get response from AI"),
        )

        response = client.post(
            self.endpoint, json={"url": "https://example.com", "question": "What is this about?"}, headers=auth_headers
        )

        assert response.json() == {"detail": "Failed to get response from AI"}
        assert response.status_code == 500

    def test_content_is_empty_on_wiki_page__returns_400(
        self, client: TestClient, auth_headers: dict[str, str], mocker: MockerFixture
    ) -> None:
        mock_response = ScrapingResponse(
            title="Test Title",
            content="",
            image_url="https://example.com/image.jpg",
            categories=["test"],
            references=["test"],
        )
        mocker.patch("scraping.router.webscrape_url", return_value=mock_response)

        response = client.post(
            self.endpoint, json={"url": "https://example.com", "question": "What is this about?"}, headers=auth_headers
        )

        assert response.json() == {"detail": "Failed to get content from URL"}
        assert response.status_code == 400

    def test_empty_url__returns_400(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        response = client.post(self.endpoint, json={"url": "", "question": "What is this about?"}, headers=auth_headers)

        assert response.json() == {
            "detail": [
                {
                    "type": "string_too_short",
                    "loc": ["body", "url"],
                    "msg": "String should have at least 1 character",
                    "input": "",
                    "ctx": {"min_length": 1},
                }
            ]
        }
        assert response.status_code == 422

    def test_empty_question__returns_400(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        response = client.post(self.endpoint, json={"url": "https://example.com", "question": ""}, headers=auth_headers)

        assert response.json() == {
            "detail": [
                {
                    "type": "string_too_short",
                    "loc": ["body", "question"],
                    "msg": "String should have at least 1 character",
                    "input": "",
                    "ctx": {"min_length": 1},
                }
            ]
        }
        assert response.status_code == 422

    def test_ask_endpoint_unauthenticated(self, client: TestClient) -> None:
        response = client.post(self.endpoint, json={"url": "https://example.com", "question": "What is this about?"})

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_ask_endpoint_incorrect_credentials(self, client: TestClient) -> None:
        credentials = "incorrect:credentials"
        encoded = base64.b64encode(credentials.encode()).decode()
        headers = {"Authorization": f"Basic {encoded}"}

        response = client.post(
            self.endpoint, json={"url": "https://example.com", "question": "What is this about?"}, headers=headers
        )

        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid credentials"}
