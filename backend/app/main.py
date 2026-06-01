from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.session import init_db
from app.routers.auth import router as auth_router
from app.routers.assignment import router as assignment_router
from app.routers.submission import router as submission_router
from app.routers.grading_result import router as grading_result_router
from app.routers.grading import router as grading_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(assignment_router)
app.include_router(submission_router)
app.include_router(grading_result_router)
app.include_router(grading_router)
@app.get("/")
async def root():
    return {
        "message": "EduMetric API Running"
    }