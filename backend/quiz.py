from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from backend import database, models, schemas
from backend.auth import oauth2_scheme
from jose import JWTError, jwt
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func
from fastapi import Cookie  # <-- Add this import
from fastapi.responses import RedirectResponse  # <-- If not already imported

router = APIRouter()

# Correct template initialization (use either one)
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "your-secret-key-123"
ALGORITHM = "HS256"

# ... rest of your existing code ...
ACCESS_TOKEN_EXPIRE_MINUTES = 30


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
        access_token: str = Cookie(None)  # Changed parameter name for clarity
):
    if not access_token:
        return RedirectResponse("/login")

    try:
        # Remove "Bearer " prefix if present
        token = access_token.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        questions = db.query(models.Question).order_by(func.random()).limit(5).all()
        return templates.TemplateResponse("dashboard.html", {"request": request, "questions": questions})
    except JWTError:
        return RedirectResponse("/login")

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