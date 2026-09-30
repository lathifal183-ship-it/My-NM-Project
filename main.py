from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.routes.web import router as web_router
from app.routes.api import router as api_router

@asynccontextmanager
async def lifespan(app:FastAPI):
    init_db()
    yield

app=FastAPI(title=settings.app_name,version="1.0.0",lifespan=lifespan)
app.add_middleware(SessionMiddleware,secret_key=settings.secret_key,same_site="lax",https_only=False)
app.add_middleware(CORSMiddleware,allow_origins=["http://127.0.0.1:8000","http://localhost:8000"],
                   allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.mount("/static",StaticFiles(directory="app/static"),name="static")
app.include_router(web_router)
app.include_router(api_router)

@app.get("/health")
def health():return {"status":"ok","service":"PocketSmart AI"}

if __name__=="__main__":
    import uvicorn
    uvicorn.run("app.main:app",host="127.0.0.1",port=8000,reload=True)
