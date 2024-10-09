from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from database import Base, engine
from controllers import router
from contextlib import asynccontextmanager

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=app_lifespan, docs_url=None, redoc_url=None)
app.add_middleware(SessionMiddleware, secret_key="mumng")
app.include_router(router)