
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    prefix="/admin",
    tags=["Admin Panel"]
)


templates = Jinja2Templates(
    directory="templates"
)


@router.get(
    "/login",
    response_class=HTMLResponse,
    include_in_schema=False
)
def admin_login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={
            "title": "ورود مدیر"
        }
    )


@router.get(
    "/",
    response_class=HTMLResponse,
    include_in_schema=False
)
def admin_dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "title": "داشبورد مدیریت"
        }
    )


@router.get(
    "/users",
    response_class=HTMLResponse,
    include_in_schema=False
)
def admin_users_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/users.html",
        context={
            "title": "مدیریت کاربران"
        }
    )


@router.get(
    "/logs",
    response_class=HTMLResponse,
    include_in_schema=False
)
def admin_logs_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/logs.html",
        context={
            "title": "گزارش رویدادها"
        }
    )


@router.get(
    "/banks",
    response_class=HTMLResponse,
    include_in_schema=False
)
def admin_banks_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/banks.html",
        context={
            "title": "مدیریت بانک‌ها"
        }
    )
