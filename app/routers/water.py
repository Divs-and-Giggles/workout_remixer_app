from fastapi.responses import RedirectResponse
from fastapi import Request, status
from app.dependencies.auth import IsUserLoggedIn, get_current_user, is_admin
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from . import router,templates
from app.models.logging import WaterIntake
from datetime import datetime, date
from sqlmodel import select

@router.get("/water")
def water_page(request: Request):
    """
    Renders water log. Used in testing and developing the water log in isolation.
    """
    return templates.TemplateResponse(
        request = request,
        name="water_log.html"
        )

@router.get("/water/today")
def get_today_water(db: SessionDep, user: AuthDep):
    today = date.today()

    records = db.exec(select(WaterIntake).where(WaterIntake.user_id == user.id)).all()

    total = 0

    for r in records:
        if r.timestamp.date() == today:
            total += r.amount_ml

    return {"total": total}

@router.post("/water/add")
def add_water(amount: int, db: SessionDep, user: AuthDep):
    """
    Adds a new entry into the water log for an authenticated user.

    Args: 
        amount (int): Water drank in ml.
        db (SessionDep): Database session dependency used for dependency injection.
        user (AuthDep): Authenticated user dependency used for dependency injection.

    Returns:
        A dictionary with a confirmation message of entry addition.
    """

    entry = WaterIntake(
        user_id= user.id,
        amount_ml=amount,
        timestamp=datetime.now()
    )

    db.add(entry)
    db.commit()

    return{"message": "added"}

@router.get("/stats")
def water_stats_page(request: Request):
    """
    Renders stats page for water intake.

    Args: 
        request (Request):  HTTP request object required to render the response.

    Returns:
        The stats page.
    """
    return templates.TemplateResponse(
        request = request,
        name="water-stats.html"
        )

@router.get("/water/weekly")
def get_weekly_water(db: SessionDep, user: AuthDep):
    """
    Calculates the total water drank for each day of the past week for an authenticated user.

    Args: 
        db (SessionDep): Database session dependency used for dependency injection.
        user (AuthDep): Authenticated user dependency used for dependency injection.

    Returns:
        A dictionary containing the water drank per day of the week(Sun - Sat).
    """

    today = date.today()

    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    result = {day: 0 for day in days}

    records = db.exec(select(WaterIntake).where(WaterIntake.user_id == user.id)).all()

    today_index = (today.weekday() + 1) % 7

    for r in records:
        d = r.timestamp.date()

        record_index = (d.weekday() + 1) % 7

        diff = today_index - record_index

        if 0 <= diff <= 6:
            day_name = days[record_index]
            result[day_name] += r.amount_ml

    return result