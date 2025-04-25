from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from backend import database, models, schemas
from backend.auth import oauth2_scheme
from jose import JWTError, jwt
from fastapi.responses import HTMLResponse
from sqlalchemy import func
import random

# Remove the prefix so we can use /dashboard directly
router = APIRouter()  # Removed prefix="/quiz"
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "your_secret_key_here"  # Should match auth.py
ALGORITHM = "HS256"


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
        request: Request,
        db: Session = Depends(get_db),
        username: str = Depends(get_current_user)  # This ensures authentication
):
    # Get 5 random questions
    questions = db.query(models.Question).order_by(func.random()).limit(5).all()

    # Make sure your Question model has these fields
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "questions": questions,
            "username": username  # Optional: pass username to template
        }
    )


@router.post("/submit")
async def submit_answers(
        answers: dict,
        db: Session = Depends(get_db),
        username: str = Depends(get_current_user)
):
    score = 0
    total = 0

    for question_id, answer in answers.items():
        q_id = int(question_id[1:])  # Extract ID from "q1", "q2" etc.
        question = db.query(models.Question).filter(models.Question.id == q_id).first()

        if question and answer == question.correct_answer:
            score += 1
        total += 1

    return {"score": score, "total": total}