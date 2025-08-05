from fastapi import FastAPI
from .api import endpoints

app = FastAPI(
    title="Medical Shift Schedule Generator",
    description="An API to generate optimal shift schedules for medical personnel.",
    version="1.0.0"
)

# Include the API router
app.include_router(endpoints.router, prefix="/api")

@app.get("/", tags=["Root"])
async def read_root():
    """A simple health check endpoint."""
    return {"status": "ok"}
