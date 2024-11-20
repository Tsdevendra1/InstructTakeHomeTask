import base64

from fastapi.testclient import TestClient
from pytest_mock import MockerFixture

from scraping.models import ScrapingResponse


class TestPOST:
    endpoint = "/scrape"

    def test_scrape_endpoint_success(
        self, client: TestClient, auth_headers: dict[str, str], mocker: MockerFixture
    ) -> None:
        test_url = "https://example.com"
        mock_response = ScrapingResponse(
            title="Test Title",
            content="Test Content",
            image_url="https://example.com/image.jpg",
            categories=["test"],
            references=["test"],
        )
        mock_scrape = mocker.patch("scraping.router.webscrape_url", return_value=mock_response)

        response = client.post(self.endpoint, json={"url": test_url}, headers=auth_headers)

        assert response.json() == {
            "title": mock_response.title,
            "content": mock_response.content,
            "image_url": mock_response.image_url,
            "categories": mock_response.categories,
            "references": mock_response.references,
        }
        assert response.status_code == 200
        mock_scrape.assert_called_once_with(test_url)

    def test_scrape_endpoint_failed_request(
        self, client: TestClient, auth_headers: dict[str, str], mocker: MockerFixture
    ) -> None:
        mock_get = mocker.patch("requests.get")
        mock_get.return_value.status_code = 404

        response = client.post(self.endpoint, json={"url": "https://example.com"}, headers=auth_headers)

        assert response.json() == {"detail": "Failed to scrape website"}
        assert response.status_code == 500

    def test_empty_url__returns_400(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        response = client.post(self.endpoint, json={"url": ""}, headers=auth_headers)

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

    def test_user_is_unauthenticated(self, client: TestClient) -> None:
        response = client.post(self.endpoint, json={"url": "https://example.com"})

        assert response.status_code == 401
        assert response.json() == {"detail": "Not authenticated"}

    def test_user_has_incorrect_credentials(self, client: TestClient) -> None:
        credentials = "incorrect:credentials"
        encoded = base64.b64encode(credentials.encode()).decode()
        headers = {"Authorization": f"Basic {encoded}"}
        response = client.post(self.endpoint, json={"url": "https://example.com"}, headers=headers)

        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid credentials"}
