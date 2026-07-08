from fastapi import FastAPI,APIRouter
import os

base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"]
)

@base_router.get("/")

async def welcome_message(): # async is better for I/O bound operations, like database queries or network requests
    app_name = os.getenv("APP_NAME")
    app_version = os.getenv("APP_VERSION")
    return {"message": f"Welcome to the {app_name} API, version {app_version} in .env!"}
