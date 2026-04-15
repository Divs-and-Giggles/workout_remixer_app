from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import status
from app.dependencies.session import SessionDep
from app.dependencies.auth import AdminDep, IsUserLoggedIn, get_current_user, is_admin
from . import router, templates

@router.get("/calculator", response_class=HTMLResponse)
async def calculator_view(
    request: Request,
    user:IsUserLoggedIn,
):
    """
    Allows the user to choose the types of calculator they want (BMI,BMR,Body Fat and Max Bench Press)
    """
    return templates.TemplateResponse(
        request,
        "calculator_home.html",
        {
            "user": user
        }
    )


@router.get("/calculator/bmi", response_class=HTMLResponse)
async def bmi_calculator(
    request: Request,
    user: IsUserLoggedIn,
):
    """
    Shows the BMI calculator page, Sets the active calculator to BMI
    """
    return templates.TemplateResponse(
        request,
        "calculator.html",
        {
            "active_calculator": "bmi",
            "user": user
        }
    )

@router.get("/calculator/bmr", response_class=HTMLResponse)
async def bmr_calculator(
    request: Request,
    user: IsUserLoggedIn,
):
    """
    Displays the BMR calculator page, Sets the active calculator to BMR
    """
    return templates.TemplateResponse(
        request,
        "calculator.html",
        {
            "active_calculator": "bmr",
            "user": user
        }
    )


@router.get("/calculator/body_fat", response_class=HTMLResponse)
async def body_fat_calculator(
    request: Request,
    user: IsUserLoggedIn,
):
    """
    Displays the body fat calculator page, Sets the active calculator to Body Fat
    """
    return templates.TemplateResponse(
        request,
        "calculator.html",
        {
            "active_calculator": "body_fat",
            "user": user
        }
    )


@router.get("/calculator/bench_press", response_class=HTMLResponse)
async def bench_press_calculator(
    request: Request,
    user: IsUserLoggedIn,
):
    """
    Displays the bench press calculator page, Sets the active calculator to Max Bench Press
    """
    return templates.TemplateResponse(
        request,
        "calculator.html",
        {
            "active_calculator": "bench_press",
            "user": user
        }
    )


