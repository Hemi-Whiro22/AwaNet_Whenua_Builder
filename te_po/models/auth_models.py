from pydantic import BaseModel


class ApiKeyInfo(BaseModel):
    customer_name: str
    api_key: str
    active: bool
    created_at: str | None = None
    last_used_at: str | None = None
