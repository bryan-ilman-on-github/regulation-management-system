# app/main.py
from fastapi import FastAPI

# Create an instance of the FastAPI class
app = FastAPI(
    title="Regulation Management System API",
    description="API for managing and querying Indonesian regulations.",
    version="0.1.0"
)

@app.get("/", tags=["Root"])
def read_root():
    """
    A simple endpoint to confirm the API is running.
    """
    return {"status": "API is running!"}