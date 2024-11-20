from pydantic import BaseModel, Field


class ScrapeRequest(BaseModel):
    url: str = Field(min_length=1, max_length=2048)  # 2048 is the max length of a URL


class ScrapingResponse(BaseModel):
    title: str
    content: str
    image_url: str
    categories: list[str]
    references: list[str]


class ScrapeAskQuestionRequest(ScrapeRequest):
    question: str = Field(min_length=1)


class ScrapeAskQuestionResponse(BaseModel):
    answer: str
