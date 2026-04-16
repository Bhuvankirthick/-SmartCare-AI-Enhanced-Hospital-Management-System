from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str
    user_id: int
    linked_id: int | None


class TokenData(BaseModel):
    user_id: int | None = None
    username: str | None = None
    role: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str
    linked_id: int | None = None


class UserOut(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    is_active: bool
    linked_id: int | None

    class Config:
        from_attributes = True
