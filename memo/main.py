from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from database import Base, engine
from controllers import router

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="mumng")
app.include_router(router)

Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

