# How to run the application

- First clone the repo `git clone https://github.com/Tsdevendra1/InstructTakeHomeTask.git`
- Update `OPENAI_API_KEY` in the .env file with the key
- Build the image `docker build -t fastapi-app .`
- Run the image `docker run --env-file .env -p 8000:8000 fastapi-app`
- Ask API: `curl -X POST http://0.0.0.0:8000/ask -H "Content-Type: application/json" -u admin:secret123 -d '{"url":"https://en.wikipedia.org/wiki/Battle_of_Hastings","question":"Where was the battle of hastings?"}'`
- Scrape API: `curl -X POST http://0.0.0.0:8000/scrape -H "Content-Type: application/json" -u admin:secret123 -d '{"url":"https://en.wikipedia.org/wiki/Battle_of_Hastings"}'`
- If you want to test yourself the credentials for the basic auth are `admin:secret123`

# Design considerations + general decisions

I tried to structure the project in a way that I would for a production application. I completed all the tasks apart
from the one for rate limiting, but this was just because I wasn't sure if you were fine with using a library for that
or whether you wanted me to implement it myself. I've tried to outline my decisions in the code itself. I also made some
assumptions like only support the english language for the scraping service. Commit history also isn't as clean as I would like but I tried to make it as clear as possible.

Features implemented:
- Basic authentication
- Scraping API
- Ask API
- Optional extras for scraping

# Running tests

- Install uv https://docs.astral.sh/uv/getting-started/installation/#standalone-installer
    - If mac: `brew install uv`
    - If mac/linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Install dependencies `uv sync`
- Run application: `uv run --env-file .env pytest .`

# Project structure

```
├── Dockerfile
├── README.md
├── auth
│   ├── __init__.py
│   └── dependencies.py
├── main.py
├── pyproject.toml
├── scraping
│   ├── __init__.py
│   ├── constants.py
│   ├── models.py
│   ├── router.py
│   └── services
│       ├── openai_service.py
│       └── scraping_service.py
├── settings.py
├── tests
│   ├── __init__.py
│   ├── conftest.py
│   ├── fixtures
│   │   └── nico-ditch.html
│   └── scraping
│       ├── routes
│       │   ├── test_ask_route.py
│       │   └── test_scraping_route.py
│       └── services
│           ├── test_openapi_service.py
│           └── test_scraping_service.py
└── uv.lock
```

# If I spent more time
This is a list of things to consider if more time was spent on the project:
- Monitoring
    - Sentry
    - Newrelic/Prometheus/Grafana
- Structured logging + logging in general
- API Versioning
- Caching (e.g. memcached/redis)
- Performance monitoring
- Test coverage
