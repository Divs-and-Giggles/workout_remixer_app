from fastapi.responses import RedirectResponse
from fastapi import Request, status
from app.dependencies.auth import IsUserLoggedIn, get_current_user, is_admin
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from . import router,templates
from app.models.logging import WeightLog
from datetime import datetime, date
from sqlmodel import select

# @router.get("/sleep")
# def sleep_page(request: Request):
#     return templates.TemplateResponse(
#         request = request,
#         name="sleep_log.html"
#         )

# @router.get("/water/today")
# def get_today_water(db: SessionDep, user: AuthDep):
#     today = date.today()

#     records = db.exec(select(WaterIntake).where(WaterIntake.user_id == user.id)).all()

#     total = 0

#     for r in records:
#         if r.timestamp.date() == today:
#             total += r.amount_ml

#     return {"total": total}

@router.post("/weight/add")
def add_weight(weight: float, db: SessionDep, user: AuthDep):
    """
    Adds a new entry into the weight log for an authenticated user. Unlike the other logs, this one is not cumulative.

    Args: 
        weight (float): Current weight.
        db (SessionDep): Database session dependency used for dependency injection.
        user (AuthDep): Authenticated user dependency used for dependency injection.

    Returns:
        A dictionary with a confirmation message of entry addition.
    """
    today = date.today()

    existing_weight = db.exec(select(WeightLog).where(WeightLog.user_id == user.id)).all()

    today_entry = None

    for entry in existing_weight:
        if entry.timestamp.date() == today:
            today_entry = entry
            break

    if today_entry:
        today_entry.weight = weight
        today_entry.timestamp = datetime.now()

    else:
        today_entry = WeightLog(
            user_id=user.id,
            weight = weight,
            timestamp=datetime.now()
        )
        db.add(today_entry)
        
    db.commit()

    return{"message": "added"}

@router.get("/weight-stats")
def weight_stats_page(request: Request):
    """
    Renders stats page for current weight.

    Args: 
        request (Request):  HTTP request object required to render the response.

    Returns:
        The stats page.
    """
        
    return templates.TemplateResponse(
        request = request,
        name="weight-stats.html"
        )

@router.get("/weight/weekly")
def get_weekly_weight(db: SessionDep, user: AuthDep):
    """
    Calculates the trend in weight fluctuations for each day of the past week for an authenticated user.

    Args: 
        db (SessionDep): Database session dependency used for dependency injection.
        user (AuthDep): Authenticated user dependency used for dependency injection.

    Returns:
        A dictionary containing the weight of the user for each day of the week(Sun - Sat).
    """

    today = date.today()

    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    result = {day: 0 for day in days}

    records = db.exec(select(WeightLog).where(WeightLog.user_id == user.id)).all()

    today_index = (today.weekday() + 1) % 7

    for r in records:
        d = r.timestamp.date()

        record_index = (d.weekday() + 1) % 7

        diff = today_index - record_index

        if 0 <= diff <= 6:
            day_name = days[record_index]
            result[day_name] += r.weight

    return result