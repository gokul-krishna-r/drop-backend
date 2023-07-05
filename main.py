from fastapi import FastAPI
from server.authentication import router as auth_router
from server.projects_auth import router as proj_router
from server.database import shutdown_db_client, startup_db_client
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Drop API",
    version="0.5.0",
)

origins = [
    "http://localhost",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, tags=["Auth"])
app.include_router(proj_router, tags=["Project"])


@app.get("/", tags=["Test"])
async def test_response():
    return "Api Start"


@app.on_event("shutdown")
def close_client():
    shutdown_db_client()
