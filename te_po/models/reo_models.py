from pydantic import BaseModel


class ReoRequest(BaseModel):
    text: str


class ReoResult(BaseModel):
    id: str
    output: str
    type: str
    saved: bool
