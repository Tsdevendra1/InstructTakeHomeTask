import logging

from fastapi import APIRouter, Depends, HTTPException

from auth.dependencies import verify_credentials
from scraping.models import ScrapeAskQuestionRequest, ScrapeAskQuestionResponse, ScrapeRequest, ScrapingResponse
from scraping.services.openai_service import get_ai_response
from scraping.services.scraping_service import webscrape_url

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(verify_credentials)])


@router.post("/scrape")
async def scrape_website(
    request: ScrapeRequest,
) -> ScrapingResponse:
    return await webscrape_url(request.url)


@router.post("/ask")
async def ask_wiki(
    request: ScrapeAskQuestionRequest,
) -> ScrapeAskQuestionResponse:
    webscrape_result = await webscrape_url(request.url)
    content = webscrape_result.content
    if content == "":
        raise HTTPException(status_code=400, detail="Failed to get content from URL")
    question = request.question
    return get_ai_response(content, question)
