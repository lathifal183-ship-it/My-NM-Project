from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.auth import create_user, authenticate, get_user_by_id
from app.services.recommendations import get_history

router=APIRouter()
templates=Jinja2Templates(directory="app/templates")

def current_user(request):
    uid=request.session.get("user_id")
    return get_user_by_id(int(uid)) if uid else None

@router.get("/",response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse("index.html",{"request":request,"user":current_user(request)})

@router.get("/register",response_class=HTMLResponse)
def register_page(request:Request):
    return templates.TemplateResponse("register.html",{"request":request,"user":current_user(request),"error":None})

@router.post("/register")
def register(request:Request,username:str=Form(...),email:str=Form(...),password:str=Form(...)):
    try:
        user=create_user(username,email,password)
        request.session["user_id"]=user["id"]
        return RedirectResponse("/dashboard",status_code=303)
    except ValueError as exc:
        return templates.TemplateResponse("register.html",{"request":request,"user":None,"error":str(exc)},status_code=400)

@router.get("/login",response_class=HTMLResponse)
def login_page(request:Request):
    return templates.TemplateResponse("login.html",{"request":request,"user":current_user(request),"error":None})

@router.post("/login")
def login(request:Request,username:str=Form(...),password:str=Form(...)):
    user=authenticate(username,password)
    if not user:
        return templates.TemplateResponse("login.html",{"request":request,"user":None,"error":"Incorrect username or password."},status_code=401)
    request.session["user_id"]=user["id"]
    return RedirectResponse("/dashboard",status_code=303)

@router.post("/logout")
def logout(request:Request):
    request.session.clear()
    return RedirectResponse("/",status_code=303)

@router.get("/dashboard",response_class=HTMLResponse)
def dashboard(request:Request):
    user=current_user(request)
    if not user:return RedirectResponse("/login",status_code=303)
    return templates.TemplateResponse("dashboard.html",{"request":request,"user":user,"history":get_history(user["id"])[:5]})

@router.get("/history",response_class=HTMLResponse)
def history_page(request:Request):
    user=current_user(request)
    if not user:return RedirectResponse("/login",status_code=303)
    return templates.TemplateResponse("history.html",{"request":request,"user":user,"history":get_history(user["id"])})

@router.get("/planner/{planner}",response_class=HTMLResponse)
def planner_page(request:Request,planner:str):
    user=current_user(request)
    if not user:return RedirectResponse("/login",status_code=303)
    if planner not in {"home","party","jewelry"}:return RedirectResponse("/dashboard",status_code=303)
    return templates.TemplateResponse("planner.html",{"request":request,"user":user,"planner":planner})
