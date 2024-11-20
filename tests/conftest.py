import base64

import pytest
from fastapi.testclient import TestClient

from main import app
from settings import settings


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def auth_headers() -> dict[str, str]:
    credentials = f"{settings.ADMIN_USERNAME}:{settings.ADMIN_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}
