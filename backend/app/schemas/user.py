from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str | None

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
