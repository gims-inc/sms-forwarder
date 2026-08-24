from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.sms.router import init_db


@asynccontextmanager
async def database_lifespan(app: FastAPI):
    await init_db()
    yield
