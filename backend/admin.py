from fastapi import Request, Depends, HTTPException, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.auth import get_db
from backend.quiz import get_current_user

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/panel", response_class=HTMLResponse)
async def admin_panel(request: Request, db: Session = Depends(get_db)):
    questions = db.query(models.Question).all()
    return templates.TemplateResponse("admin_panel.html", {"request": request, "questions": questions})


@router.post("/add-question")
async def add_question(
        question: schemas.QuestionCreate,
        db: Session = Depends(get_db),
        admin: str = Depends(get_current_user)
):
    # Verify admin
    db_admin = db.query(models.Admin).filter(models.Admin.name == admin).first()
    if not db_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    new_question = models.Question(
        category=question.category,
        question_text=question.question_text,
        correct_answer=question.correct_answer
    )
    db.add(new_question)
    db.commit()
    return {"message": "Question added successfully"}