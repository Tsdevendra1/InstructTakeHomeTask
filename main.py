from fastapi import FastAPI

from scraping.router import router

app = FastAPI()
app.include_router(router)
