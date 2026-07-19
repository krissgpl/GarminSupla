from pydantic import BaseModel, HttpUrl


class SetupForm(BaseModel):
    """Setup wizard form data."""

    server: HttpUrl
