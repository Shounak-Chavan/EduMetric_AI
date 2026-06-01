from pydantic import BaseModel, Field


class SessionTokenRequest(BaseModel):
    token: str = Field(min_length=1)


class MessageResponse(BaseModel):
    message: str