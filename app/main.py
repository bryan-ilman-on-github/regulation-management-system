from fastapi import FastAPI
from .core.database import engine, Base
from .models import regulation, user
from .api.endpoints import regulations, auth

# # This line creates the table if it doesn't exist
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Regulation Management System API",
    description="API for managing and querying Indonesian regulations.",
    version="0.1.0"
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(regulations.router, prefix="/api/v1/regulations", tags=["Regulations"])

@app.get("/", tags=["Root"])
def read_root():
    """
    A simple endpoint to confirm the API is running.
    """
    return {"status": "API is running!"}