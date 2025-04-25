from fastapi import APIRouter, Depends, HTTPException, Request, Cookie
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from backend import database, models
from backend.auth import oauth2_scheme
from sqlalchemy import func

router = APIRouter()
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "your-secret-key-123"  # Must match auth.py
ALGORITHM = "HS256"


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Add this to quiz.py (before the router definitions)
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
        access_token: str = Cookie(None),
        db: Session = Depends(get_db)
):
    if not access_token:
        return RedirectResponse("/login")

    try:
        token = access_token.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return RedirectResponse("/login")

        questions = db.query(models.Question).order_by(func.random()).limit(5).all()
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "questions": questions, "username": username}
        )
    except JWTError:
        return RedirectResponse("/login")


@router.post("/submit")
async def submit_answers(
        answers: dict,
        db: Session = Depends(get_db),
        access_token: str = Cookie(None)
):
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        token = access_token.replace("Bearer ", "")
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        score = 0
        total = 0
        for question_id, answer in answers.items():
            q_id = int(question_id[1:])
            question = db.query(models.Question).filter(models.Question.id == q_id).first()
            if question and answer == question.correct_answer:
                score += 1
            total += 1

        return {"score": score, "total": total}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")