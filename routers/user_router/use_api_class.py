from pydantic import BaseModel, Field


class RegisterBody(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    email: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1)
    color: str | None = Field(default=None, max_length=7)


class RegisterResponse(BaseModel):
    id: int
    username: str
    email: str
