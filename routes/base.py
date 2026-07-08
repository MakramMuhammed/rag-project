from fastapi import FastAPI,APIRouter, Depends
import os
from helpers.config import get_settings


base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"]
)

@base_router.get("/")

async def welcome_message(settings=Depends(get_settings)): # async is better for I/O bound operations, like database queries or network requests
    #settings = get_settings()
    app_name = settings.APP_NAME
    app_version = settings.APP_VERSION
    return {"message": f"Welcome to the {app_name} API, version {app_version} in .env!"}
