from pydantic import BaseModel


class AdminAccount(BaseModel):
    username: str
    password_hash: str
    created_at: str
    enabled: bool = True
