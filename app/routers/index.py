from fastapi.responses import RedirectResponse
from fastapi import Request, status
from app.dependencies.auth import IsUserLoggedIn, get_current_user, is_admin
from app.dependencies.session import SessionDep
from app.dependencies.auth import AuthDep
from . import router,templates
from app.models.logging import WaterIntake
from datetime import datetime, date
from sqlmodel import select

@router.get("/", response_class=RedirectResponse)
async def index_view(
    request: Request,
    user_logged_in: IsUserLoggedIn,
    db: SessionDep
):
    if user_logged_in:
        user = await get_current_user(request, db)
        if await is_admin(user):
            return RedirectResponse(url=request.url_for('admin_home_view'), status_code=status.HTTP_303_SEE_OTHER)
        return RedirectResponse(url=request.url_for('home_view'), status_code=status.HTTP_303_SEE_OTHER)
    response = RedirectResponse(url=request.url_for('login_view'), status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(
        key="access_token", 
        httponly=True,
        samesite="none",
        secure=True
    )
    return response

#Color scheme
#color: #1C1919;
#color: #9A9996;
#color: #CFCFCC;
#color: #F3F3E9;
#color: #D51313;


 
# @router.post("/water/add")
# def add_water_log(amount: int, db: SessionDep, user: AuthDep):
#     entry = WaterIntake(
#         user_id= user.id,
#         amount_ml=amount,
#         timestamp=datetime.now()
#     )

#     db.add(entry)
#     db.commit()

#     return {"message": "Water added"}

# @router.get("/water/today")
# def get_today(db: SessionDep, user: AuthDep):
#     today = datetime.now().date()
#     total = 0

#     entries = db.exec(select(WaterIntake)).all()

#     for entry in entries:
#         if entry.user_id ==user.id:
#             if entry.timestamp.date() == today:
#                 total+= entry.amount_ml

#     return {"total": total}