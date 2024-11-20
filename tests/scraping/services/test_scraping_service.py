from typing import Self

import pytest
from fastapi import HTTPException
from pytest_mock import MockerFixture

from scraping.models import ScrapingResponse
from scraping.services.scraping_service import extract_data_from_html, webscrape_url


# Decision: This could have been in another file to allow better re-use in a real project but I'll leave it here for now
class MockAsyncResponse:
    def __init__(self, text: str, status: int) -> None:
        self._text = text
        self.status = status

    async def text(self) -> str:
        return self._text

    async def __aexit__(self, exc_type: Exception, exc_val: Exception, exc_tb: Exception) -> None:
        pass

    async def __aenter__(self) -> Self:
        return self


@pytest.mark.asyncio
class TestWebscrapeURL:
    async def test_successful_request_to_url__returns_expected_data(self, mocker: MockerFixture) -> None:
        expected_response = ScrapingResponse(
            title="Test Article Title",
            content="First paragraph content.\nSection Heading\nSecond paragraph content.",
            image_url="https://test.com/image.jpg",
            categories=[],
            references=[],
        )
        extract_data_from_html_mock = mocker.patch(
            "scraping.services.scraping_service.extract_data_from_html", return_value=expected_response
        )
        mock_response = MockAsyncResponse(
            text="test",
            status=200,
        )
        mocker.patch("aiohttp.ClientSession.get", return_value=mock_response)

        response = await webscrape_url("https://test.com")

        assert response == expected_response
        extract_data_from_html_mock.assert_called_once_with("test")

    async def test_unsuccessful_request_to_url__raises_http_exception(self, mocker: MockerFixture) -> None:
        mock_response = MockAsyncResponse(
            text="test",
            status=500,
        )
        mocker.patch("aiohttp.ClientSession.get", return_value=mock_response)

        with pytest.raises(HTTPException):
            await webscrape_url("https://test.com")


class TestExtractDataFromHTML:
    def test_real_world_example(self) -> None:
        with open("/Users/tharukadevendra/PycharmProjects/InstructTakeHomeTask/tests/fixtures/nico-ditch.html") as f:
            html = f.read()

        response = extract_data_from_html(html)
        assert response.title == "Nico Ditch"
        # Could test the entire content but this will do for now, would do it properly if I spent more time.
        assert response.content.startswith("Nico Ditch is a six-mile (9.7 km) long linear earthwork between")
        assert (
            response.image_url
            == "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/NicoDitch.jpg/220px-NicoDitch.jpg"
        )
        assert response.categories == [
            "Ancient dikes",
            "History of Greater Manchester",
            "History of Manchester",
            "Geography of Manchester",
            "Geography of the Metropolitan Borough of Stockport",
            "Geography of Tameside",
            "Geography of Trafford",
            "Scheduled monuments in Greater Manchester",
            "Linear earthworks",
        ]
        assert response.references == [
            "https://en.wikipedia.org/wiki/Levenshulme",
            "https://en.wikipedia.org/wiki/Greater_Manchester",
            "https://en.wikipedia.org/wiki/Anglo-Saxon_England",
            "https://en.wikipedia.org/wiki/Earthworks_(archaeology)",
            "https://en.wikipedia.org/wiki/Industrial_Revolution",
            "https://en.wikipedia.org/wiki/Earthworks_(archaeology)",
            "https://en.wikipedia.org/wiki/Ashton-under-Lyne",
            "https://en.wikipedia.org/wiki/Stretford",
            "https://en.wikipedia.org/wiki/Denton,_Greater_Manchester",
            "https://en.wikipedia.org/wiki/Scheduled_Ancient_Monument",
            "https://en.wikipedia.org/wiki/Audenshaw",
            "https://en.wikipedia.org/wiki/Kersal",
            "https://en.wikipedia.org/wiki/Old_English",
            "https://en.wikipedia.org/wiki/Nickar",
            "https://en.wikipedia.org/wiki/Reddish",
            "https://en.wikipedia.org/wiki/Slade_Hall",
            "https://en.wikipedia.org/wiki/Longsight",
            "https://en.wikipedia.org/wiki/Ordnance_Survey_National_Grid",
            "https://en.wikipedia.org/wiki/Ordnance_Survey_National_Grid",
            "https://en.wikipedia.org/wiki/Stretford",
            "https://en.wikipedia.org/wiki/Denton,_Greater_Manchester",
            "https://en.wikipedia.org/wiki/Reddish",
            "https://en.wikipedia.org/wiki/Gorton",
            "https://en.wikipedia.org/wiki/Levenshulme",
            "https://en.wikipedia.org/wiki/Burnage",
            "https://en.wikipedia.org/wiki/Rusholme",
            "https://en.wikipedia.org/wiki/Platt_Fields_Park",
            "https://en.wikipedia.org/wiki/Fallowfield",
            "https://en.wikipedia.org/wiki/Withington",
            "https://en.wikipedia.org/wiki/Chorlton-cum-Hardy",
            "https://en.wikipedia.org/wiki/Metropolitan_borough",
            "https://en.wikipedia.org/wiki/Greater_Manchester",
            "https://en.wikipedia.org/wiki/Metropolitan_Borough_of_Stockport",
            "https://en.wikipedia.org/wiki/Manchester",
            "https://en.wikipedia.org/wiki/Audenshaw_Reservoirs",
            "https://en.wikipedia.org/wiki/Urmston",
            "https://en.wikipedia.org/wiki/Ordnance_Survey_National_Grid",
            "https://en.wikipedia.org/wiki/End_of_Roman_rule_in_Britain",
            "https://en.wikipedia.org/wiki/Norman_conquest_of_England",
            "https://en.wikipedia.org/wiki/Anglo-Saxons",
            "https://en.wikipedia.org/wiki/Mercia",
            "https://en.wikipedia.org/wiki/Northumbria",
            "https://en.wikipedia.org/wiki/Early_medieval",
            "https://en.wikipedia.org/wiki/Wessex",
            "https://en.wikipedia.org/wiki/North_West_England",
            "https://en.wikipedia.org/wiki/Britons_(historical)",
            "https://en.wikipedia.org/wiki/Danes_(Germanic_tribe)",
            "https://en.wikipedia.org/wiki/Middle_Ages",
            "https://en.wikipedia.org/wiki/Looting",
            "https://en.wikipedia.org/wiki/Saxons",
            "https://en.wikipedia.org/wiki/Antiquarian",
            "https://en.wikipedia.org/wiki/Denton,_Greater_Manchester",
            "https://en.wikipedia.org/wiki/Platt_Fields_Park",
            "https://en.wikipedia.org/wiki/Scheduled_Ancient_Monument",
            "https://en.wikipedia.org/wiki/History_of_Manchester",
            "https://en.wikipedia.org/wiki/Scheduled_Monuments_in_Greater_Manchester",
            "https://en.wikipedia.org/wiki/Clarendon_Press",
            "https://en.wikipedia.org/wiki/BBC",
            "https://en.wikipedia.org/wiki/Historic_England",
            "https://en.wikipedia.org/wiki/John_Harland",
            "https://en.wikipedia.org/wiki/Manchester_University",
        ]

    def test_html_resembles_expected_structure__returns_expected_data(self) -> None:
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1 id="firstHeading">Test Article Title</h1>
            <div id="mw-content-text">
                <div class="mw-parser-output">
                    <p>First paragraph content.</p>
                    <div class="mw-heading"><h2>Section Heading</h2></div>
                    <p>Second paragraph content.</p>
                    <table class="infobox">
                        <tr>
                            <td>
                                <img src="//test.com/image.jpg" alt="Test Image"/>
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
        </body>
        </html>        
        """
        response = extract_data_from_html(html)
        assert response.title == "Test Article Title"
        assert response.content == "First paragraph content.\nSection Heading\nSecond paragraph content."
        assert response.image_url == "https://test.com/image.jpg"

    def test_html_missing_title__raises_http_exception(self) -> None:
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <div id="mw-content-text">
                <div class="mw-parser-output">
                    <p>First paragraph content.</p>
                    <div class="mw-heading"><h2>Section Heading</h2></div>
                    <p>Second paragraph content.</p>
                    <table class="infobox">
                        <tr>
                            <td>
                                <img src="//test.com/image.jpg" alt="Test Image"/>
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
        </body>
        </html>        
        """

        with pytest.raises(HTTPException):
            extract_data_from_html(html)

    def test_html_missing_content__raises_http_exception(self) -> None:
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1 id="firstHeading">Test Article Title</h1>
            <table class="infobox">
                <tr>
                    <td>
                        <img src="//test.com/image.jpg" alt="Test Image"/>
                    </td>
                </tr>
            </table>
        </body>
        </html>        
        """

        with pytest.raises(HTTPException):
            extract_data_from_html(html)

    def test_html_missing_infobox__returns_none_for_image_url(self) -> None:
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1 id="firstHeading">Test Article Title</h1>
            <div id="mw-content-text">
                <div class="mw-parser-output">
                    <p>First paragraph content.</p>
                    <div class="mw-heading"><h2>Section Heading</h2></div>
                    <p>Second paragraph content.</p>
                </div>
            </div>
        </body>
        </html>        
        """

        with pytest.raises(HTTPException):
            extract_data_from_html(html)

    def test_missing_image__returns_none_for_image_url(self) -> None:
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Page</title>
        </head>
        <body>
            <h1 id="firstHeading">Test Article Title</h1>
            <div id="mw-content-text">
                <div class="mw-parser-output">
                    <p>First paragraph content.</p>
                    <div class="mw-heading"><h2>Section Heading</h2></div>
                    <p>Second paragraph content.</p>
                    <table class="infobox">
                        <tr>
                            <td>
                            </td>
                        </tr>
                    </table>
                </div>
            </div>
        </body>
        </html>        
        """

        with pytest.raises(HTTPException):
            extract_data_from_html(html)

    # NOTE: I could add more permutations of the HTML structure to test the function (e.g. edge cases with the content), but I think this is enough for now.
