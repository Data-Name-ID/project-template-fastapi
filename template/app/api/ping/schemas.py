from pydantic import BaseModel


class PingPublic(BaseModel):
    ping: str = "pong"
