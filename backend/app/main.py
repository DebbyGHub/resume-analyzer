from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.core.database import engine, Base

from backend.app.api import health, resume
from backend.app.api.routes import interview
from backend.app.api.routes import questions

# Import models so SQLAlchemy registers them before table creation
import backend.app.models.orm_models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "http://localhost:5174",
                   "https://resume-analyzer-six-flax.vercel.app"
                   ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Existing routes
app.include_router(health.router, prefix="/api")
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])

# Interview evaluation routes
app.include_router(
    interview.router,
    prefix="/api/interview",
    tags=["interview"],
)

app.include_router(
    questions.router,
    prefix="/api/interview",
    tags=["interview"],
)