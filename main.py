from fastapi import FastAPI
app = FastAPI()

@app.get("/welcome_message")

def welcome_message():
    return {"message": "Welcome to the RAG Project API!"}

