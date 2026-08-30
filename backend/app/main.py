from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import goals, skills, roadmap, resources, quiz, progress, feedback, mentor, recommendations

settings = get_settings()

app = FastAPI(title="Pathwise AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:3000",
        "https://*.vercel.app",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(goals.router, prefix="/api/goals", tags=["goals"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(roadmap.router, prefix="/api/roadmap", tags=["roadmap"])
app.include_router(resources.router, prefix="/api/resources", tags=["resources"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
app.include_router(mentor.router, prefix="/api/mentor", tags=["mentor"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}
