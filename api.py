from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models import UserCreate, HomeRequest, PartyRequest
from app.services.auth import create_user, authenticate, create_access_token, decode_token, get_user_by_id
from app.services.recommendations import recommend, save_history, get_history

router=APIRouter(prefix="/api")

def require_user(request:Request):
    uid=request.session.get("user_id")
    if uid:
        user=get_user_by_id(int(uid))
        if user:return user
    auth=request.headers.get("Authorization","")
    if auth.startswith("Bearer "):
        try:
            data=decode_token(auth[7:])
            user=get_user_by_id(int(data["sub"]))
            if user:return user
        except Exception:pass
    raise HTTPException(status_code=401,detail="Log in to use this feature.")

@router.post("/register")
def api_register(data:UserCreate):
    try:return create_user(data.username,data.email,data.password)
    except ValueError as exc:raise HTTPException(status_code=409,detail=str(exc))

@router.post("/login")
def api_login(data:OAuth2PasswordRequestForm=Depends()):
    user=authenticate(data.username,data.password)
    if not user:raise HTTPException(status_code=401,detail="Incorrect username or password.")
    return {"access_token":create_access_token(user),"token_type":"bearer","user":user}

@router.post("/logout")
def api_logout(request:Request):
    request.session.clear()
    return {"message":"Logged out."}

@router.get("/token")
def token_info(user=Depends(require_user)):
    return {"authenticated":True,"user":user}

@router.get("/session-info")
def session_info(user=Depends(require_user)):
    return {"user_id":user["id"],"username":user["username"],"logged_in":True}

@router.get("/session-data")
def session_data(user=Depends(require_user)):
    return {"user":user,"history_count":len(get_history(user["id"]))}

def run(planner,payload,user,image_bytes=None,mime="image/jpeg"):
    result=recommend(planner,payload,image_bytes,mime)
    save_history(user["id"],planner,payload,result)
    return result

@router.post("/generate-home")
def generate_home(data:HomeRequest,user=Depends(require_user)):
    return run("home",data.model_dump(),user)

@router.post("/generate-party")
def generate_party(data:PartyRequest,user=Depends(require_user)):
    return run("party",data.model_dump(),user)

@router.post("/generate-jewelry")
async def generate_jewelry(request:Request,total_budget:float=Form(...),occasion:str=Form(...),
    preferences:str=Form("Any"),outfit_description:str=Form(""),additional_requirements:str=Form(""),
    outfit_image:UploadFile|None=File(default=None),user=Depends(require_user)):
    if total_budget<=0:raise HTTPException(status_code=422,detail="Budget must be greater than zero.")
    image_bytes=None;mime="image/jpeg"
    if outfit_image and outfit_image.filename:
        if outfit_image.content_type not in {"image/jpeg","image/png","image/webp"}:
            raise HTTPException(status_code=415,detail="Upload JPG, PNG or WEBP.")
        image_bytes=await outfit_image.read()
        if len(image_bytes)>5*1024*1024:raise HTTPException(status_code=413,detail="Image must be 5 MB or smaller.")
        mime=outfit_image.content_type
    payload={"total_budget":total_budget,"occasion":occasion,"preferences":preferences,
      "outfit_description":outfit_description,"additional_requirements":additional_requirements,
      "image_attached":bool(image_bytes)}
    return run("jewelry",payload,user,image_bytes,mime)

@router.get("/history")
def api_history(user=Depends(require_user)):
    return {"history":get_history(user["id"])}
