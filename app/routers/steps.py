from fastapi.responses import RedirectResponse
from fastapi import Request, status
from app.dependencies.auth import IsUserLoggedIn, get_current_user, is_admin
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from . import router,templates
from app.models.logging import StepsLog
from datetime import datetime, date
from sqlmodel import select

@router.get("/steps")
def steps_page(request: Request):
    return templates.TemplateResponse(
        request = request,
        name="steps_log.html"
    )

@router.post("/steps/add")
def add_steps(steps: int, db: SessionDep, user: AuthDep):
    entry = StepsLog(
        user_id=user.id,
        steps = steps,
        timestamp=datetime.now()
    )

    db.add(entry)
    db.commit()

    return{"message": "added"}

@router.get("/steps-stats")
def steps_stats_page(request: Request):
    return templates.TemplateResponse(
        request = request,
        name="steps-stats.html"
    )

@router.get("/steps/weekly")
def get_weekly_steps(db: SessionDep, user: AuthDep):
    today = date.today()

    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    result = {day: 0 for day in days}

    records = db.exec(select(StepsLog).where(StepsLog.user_id == user.id)).all()

    today_index = (today.weekday() + 1) % 7

    for r in records:
        d = r.timestamp.date()

        record_index = (d.weekday() + 1) % 7

        diff = today_index - record_index

        if 0 <= diff <= 6:
            day_name = days[record_index]
            result[day_name] += r.steps

    return result