from dataclasses import dataclass
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from permitta_opa_client import PermittaOpaClient

router = APIRouter(prefix="/opa")
templates = Jinja2Templates(directory="app/static/dist")
opa_client = PermittaOpaClient()

@router.get("/")
def index(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/policies/update")
def update_opa_policies(request: Request):
    opa_client.update_policies()
    opa_client.update_policy_data()

    return "OK done"
