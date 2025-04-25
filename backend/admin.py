from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import models, schemas, database
from backend.quiz import get_current_user  # Import from quiz.py
from datetime import timedelta
from backend.auth import create_access_token, verify_password
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/admin", tags=["Admin"])


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/login")
def admin_login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    admin = db.query(models.Admin).filter(models.Admin.name == form_data.username).first()
    if not admin or not verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect admin credentials")

    token = create_access_token(
        data={"sub": admin.name},
        expires_delta=timedelta(minutes=30)
    )
    return {"access_token": token, "token_type": "bearer"}


@router.post("/add-question")
def add_question(
        question: schemas.QuestionCreate,
        db: Session = Depends(get_db),
        current_user: str = Depends(get_current_user)  # Now properly imported
):
    # Verify admin privileges
    admin = db.query(models.Admin).filter(models.Admin.name == current_user).first()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    new_question = models.Question(
        category=question.category,
        question_text=question.question_text,
        correct_answer=question.correct_answer
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question