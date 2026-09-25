"""FastAPI application assembly."""

from __future__ import annotations

import pymysql
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .database import fetch_one
from .routers.auth import router as auth_router
from .routers.auth import users_router
from .routers.dashboard import router as dashboard_router
from .routers.resources import ALL_ROUTERS
from .security import success

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="药店管理系统后端 API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": str(exc.detail), "data": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": "请求参数校验失败", "data": exc.errors()},
    )


@app.exception_handler(pymysql.MySQLError)
async def database_exception_handler(
    _request: Request, _exc: pymysql.MySQLError
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "数据库操作失败", "data": None},
    )


@app.get("/")
def root() -> dict:
    return success(
        {
            "name": settings.app_name,
            "version": "1.0.0",
            "docs": "/docs",
        }
    )


@app.get("/health")
def health() -> dict:
    row = fetch_one("SELECT DATABASE() AS database_name, VERSION() AS version")
    return success({"status": "ok", **(row or {})})


for resource_router in ALL_ROUTERS:
    app.include_router(resource_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(dashboard_router)
