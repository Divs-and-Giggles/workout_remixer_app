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
    """
    Renders steps log. Used in testing and developing the steps log in isolation.
    """
    return templates.TemplateResponse(
        request = request,
        name="steps_log.html"
    )

@router.post("/steps/add")
def add_steps(steps: int, db: SessionDep, user: AuthDep):
    """
    Adds a new entry into the steps log for an authenticated user.

    Args: 
        steps (int): Steps taken.
        db (SessionDep): Database session dependency used for dependency injection.
        user (AuthDep): Authenticated user dependency used for dependency injection.

    Returns:
        A dictionary with a confirmation message of entry addition.
    """

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
    """
    Renders stats page for steps taken.

    Args: 
        request (Request):  HTTP request object required to render the response.

    Returns:
        The stats page.
    """
    return templates.TemplateResponse(
        request = request,
        name="steps-stats.html"
    )

@router.get("/steps/weekly")
def get_weekly_steps(db: SessionDep, user: AuthDep):
    """
    Calculates the total steps taken for each day of the past week for an authenticated user.

    Args: 
        db (SessionDep): Database session dependency used for dependency injection.
        user (AuthDep): Authenticated user dependency used for dependency injection.

    Returns:
        A dictionary containing the steps taken per day of the week(Sun - Sat).
    """

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