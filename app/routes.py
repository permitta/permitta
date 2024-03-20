from dataclasses import dataclass
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="app/static/dist")

@router.get("/")
def index(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/users")
def index(request: Request):
    @dataclass
    class User:
        first_name: str
        last_name: str
        user_name: str
        source: str

    users: list[User] = [
        User(first_name="John-Paul", last_name="Jones", user_name="johnpauljones", source="IdentityNow"),
        User(first_name="Jimmy", last_name="Page", user_name="jimmypage", source="IdentityNow"),
        User(first_name="John", last_name="Bonham", user_name="johnbonham", source="IdentityNow"),
        User(first_name="Robert", last_name="Plant", user_name="robertplant", source="Active Directory"),
    ]

    return templates.TemplateResponse("users.html", {"request": request, "users": users})
