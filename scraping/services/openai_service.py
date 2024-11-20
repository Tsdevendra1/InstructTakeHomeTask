from fastapi import HTTPException
from openai import OpenAI

from scraping.models import ScrapeAskQuestionResponse
from settings import settings


def get_ai_response(content: str, question: str) -> ScrapeAskQuestionResponse:
    if content == "" or question == "":
        # Could possibly be a 422, but I think 400 is fine for this
        raise HTTPException(status_code=400, detail="Content and question cannot be empty")

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = f"""Based on the following Wikipedia content, please answer the question.
        Answer directly and concisely. If the answer cannot be found in the content, say so.

        Content:
        {content}

        Question: {question}"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that answers questions based on provided Wikipedia content. Only use the provided content to answer questions.",
                },
                {"role": "user", "content": prompt},
            ],
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to get response from AI")

    response_content = response.choices[0].message.content
    if response_content is None or response_content == "":
        answer = "No answer found in content"
    else:
        answer = response_content
    return ScrapeAskQuestionResponse(answer=answer)
