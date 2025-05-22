from pydantic import BaseModel


class MessageScheme(BaseModel):
    message: str = "ok"


class DetailScheme(BaseModel):
    detail: str
