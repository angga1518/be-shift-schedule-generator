
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import endpoints


app = FastAPI(
    title="Medical Shift Schedule Generator",
    description="An API to generate optimal shift schedules for medical personnel.",
    version="1.0.0"
)

# CORS settings
origins = [
    "http://localhost:3000",
    "https://laras-shift.erlangga.xyz"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Include the API router
app.include_router(endpoints.router, prefix="/api")


@app.get("/", tags=["Root"])
async def read_root():
    """A simple health check endpoint."""
    return {"status": "ok"}
