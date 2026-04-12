from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session, select
from pydantic import BaseModel
from app.database import get_session
from app.models import Routine
from app.templates import templates

router = APIRouter(prefix="/routine", tags=["Routine"])

class RoutineCreate(BaseModel):
    name: str
    difficulty: str = "beginner"
    is_generated: bool = False


class RoutineUpdate(BaseModel):
    name: str

@router.get("")
def redirect_to_slash():
    return RedirectResponse(url="/routines/")

@router.get("/", response_class=HTMLResponse)
def routines_page(request: Request, session: Session = Depends(get_session)):
    routines = session.exec(select(Routine)).all()

    return templates.TemplateResponse("routine.html", {
        "request": request,
        "routines": routines
    })

# CREATE ROUTINE

@router.post("/")
def create_routine(data: RoutineCreate, session: Session = Depends(get_session)):
    routine = Routine(
        name=data.name,
        difficulty=data.difficulty,
        is_generated=data.is_generated
    )

    session.add(routine)
    session.commit()
    session.refresh(routine)

    return routine

# DELETE ROUTINE

@router.delete("/{id}")
def delete_routine(id: int, session: Session = Depends(get_session)):
    routine = session.get(Routine, id)

    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    session.delete(routine)
    session.commit()

    return {"message": "Routine deleted successfully"}

# UPDATE ROUTINE

@router.put("/{id}")
def update_routine(id: int, data: RoutineUpdate, session: Session = Depends(get_session)):
    routine = session.get(Routine, id)

    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    routine.name = data.name

    session.add(routine)
    session.commit()
    session.refresh(routine)

    return routine

@router.get("/{id}", response_class=HTMLResponse)
def view_routine(id: int, request: Request, session: Session = Depends(get_session)):
    routine = session.get(Routine, id)

    if not routine:
        raise HTTPException(status_code=404, detail="Routine not found")

    return templates.TemplateResponse("routine_detail.html", {
        "request": request,
        "routine": routine
    })