from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class AdminLogin(BaseModel):
    name: str
    password: str

class TokenData(BaseModel):
    username: str | None = None

class UserOut(BaseModel):
    id: int
    username: str
    class Config:
        from_attributes = True

class QuestionOut(BaseModel):
    id: int
    category: str
    question_text: str
    class Config:
        from_attributes = True

class QuestionCreate(BaseModel):
    category: str
    question_text: str
    correct_answer: str