import re

import aiohttp
from bs4 import BeautifulSoup, Tag
from fastapi import HTTPException

from scraping.constants import WIKIPEDIA_SUBJECT_NAMESPACES
from scraping.models import ScrapingResponse


async def webscrape_url(url: str) -> ScrapingResponse:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise HTTPException(status_code=500, detail="Failed to scrape website")

            text = await response.text()
            return extract_data_from_html(text)


# Decision: Separate function for extracting the data so I can unit test this easier using pytest later
def extract_data_from_html(html: str) -> ScrapingResponse:
    soup = BeautifulSoup(html, "html5lib")

    title = _find_page_title(soup)
    content = _find_page_content(soup)
    image_url = _find_main_image_url(soup)
    categories = _find_categories(soup)
    references = _find_wiki_references(soup)

    # Decision: dealing with errors in this function instead of the lower level functions like _find_page_title, _find_page_content, _find_main_image_url
    # makes it easier to manage the error handling in one place.
    if image_url is None or content is None or title is None:
        # Decision: this is quite primitive error handling, we could technically return None for the fields, but I just
        # left like this for now. Could have spent more time on this if it was a real-world scenario, and depending on
        # the requirements
        raise HTTPException(status_code=500, detail="Failed to scrape website")

    return ScrapingResponse(
        title=title, content=content, image_url=image_url, categories=categories, references=references
    )


def _find_page_title(soup: BeautifulSoup) -> str | None:
    # Looking at a random wiki page e.g. (https://en.wikipedia.org/wiki/Battle_of_Hastings), they seem to use an id of "firstHeading" as the title
    # Finding by this id is a naive approach, but it should work for most wiki pages. Will have to text a few pages to see if this is consistent.
    title = soup.find(id="firstHeading")
    if title is None:
        return None
    return title.get_text().strip()


def _find_page_content(soup: BeautifulSoup) -> str | None:
    # Content seems to always be inside the div with id "mw-content-text" so this will be the starting point
    top_level_text_element = soup.find(id="mw-content-text")
    if top_level_text_element is None:
        return None

    # Within that there seems to always be a div with class "mw-parser-output" which contains the main content
    # This is a bit more risky as it's a class, but it seems to be consistent across pages
    div = top_level_text_element.find("div", class_="mw-parser-output")
    if div is None:
        return None

    last_p = None
    for element in div.find_all(["p"]):
        if element.get_text().strip():  # Only consider non-empty paragraphs
            last_p = element

    if not last_p:
        return None

    texts = []
    # Loop through all the immediate children of the div, and add the text of the p tags and mw-heading tags since this
    # is where the main content seems to be
    for child in div.children:
        if isinstance(child, Tag):
            classes = child.get("class", [])
            if "mw-heading" in classes or child.name == "p":
                text = child.get_text().strip()
                # Don't add empty strings
                if text == "":
                    continue
                cleaned_text = _clean_text(text)
                texts.append(cleaned_text)

            # This is probably a fragile way to determine when to stop, but it seems to work for now. I chose this method
            # because it avoids all the sections afterwards like "See also", "References", etc.
            if child == last_p:
                break

    # Add new lines for easier reading
    total_text_content_joined = "\n".join(texts)
    return total_text_content_joined


def _clean_text(text: str) -> str:
    """
    Do all the processing to make sure we only have the text, I think this is maybe a bit hacky and also doesn't cover
    all edge cases but it will do for now.
    """
    # Remove letter references [a], [b], etc.
    text = re.sub(r"\[[a-z]+\]", "", text)

    # Remove section header [edit] tags
    text = re.sub(r"\[edit\]", "", text)

    # Remove reference numbers [1], [2], etc.
    text = re.sub(r"\[\d+\]", "", text)

    # Remove other common Wikipedia artifacts
    text = re.sub(r"\[citation needed\]", "", text)
    text = re.sub(r"\[note \d+\]", "", text)
    text = re.sub(r"\[clarification needed\]", "", text)

    # Convert special Unicode spaces to regular spaces
    text = text.replace("\xa0", " ")

    return text


def _find_main_image_url(soup: BeautifulSoup) -> str | None:
    info_box = soup.find("table", class_="infobox")
    if not info_box:
        return None

    image = info_box.find("img")
    if not image:
        return None

    src = image.get("src")
    # src always seems to start with // so we need to add https: to make it a valid url
    return f"https:{src}"


def _find_categories(soup: BeautifulSoup) -> list[str]:
    # Categories are always in a div with id "mw-normal-catlinks"
    categories_div = soup.find(id="mw-normal-catlinks")
    if not categories_div:
        return []

    categories = []
    for link in categories_div.find_all("a"):
        category = link.get_text()
        # Checking href instead of text because this allows us to support other langauges
        if link.get("href", "").endswith(":Category"):
            continue
        categories.append(category)
    return categories


def _find_wiki_references(soup: BeautifulSoup) -> list[str]:
    # Assumption: I'm assuming that references are always in the main content div
    content_div = soup.find(id="mw-content-text")
    if not content_div:
        return []

    parser_output = content_div.find("div", class_="mw-parser-output")
    if not parser_output:
        return []

    references = []
    for link in parser_output.find_all("a"):
        # Decision: I think there still might be some edge cases with this logic, but I think it should be good enough
        # for now
        href = link.get("href", "")

        if not href.startswith("/wiki/") or href == "/wiki/ISBN_(identifier)":
            continue

        if any(namespace in href for namespace in WIKIPEDIA_SUBJECT_NAMESPACES):
            continue

        full_url = f"https://en.wikipedia.org{href}"
        references.append(full_url)

    return references
