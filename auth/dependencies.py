import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from settings import settings

security = HTTPBasic()


# Decision: Using Basic Auth here for simplicity in this example. In a production application,
# I would use JWTs
async def verify_credentials(credentials: Annotated[HTTPBasicCredentials, Depends(security)]) -> None:
    is_username_correct = secrets.compare_digest(credentials.username, settings.ADMIN_USERNAME)
    is_password_correct = secrets.compare_digest(credentials.password, settings.ADMIN_PASSWORD)
    if not (is_username_correct and is_password_correct):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
