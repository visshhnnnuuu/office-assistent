from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.db import init_db, SessionLocal
from backend.app.db.seed_data import seed_sample_knowledge_base
from backend.app.api import (
    chat_router, auth_router, memory_router,
    documents_router, tickets_router, datasets_router, evaluation_router
)

app = FastAPI(
    title=settings.project_name,
    description="Enterprise multilingual AI assistant with RBAC-guarded RAG, IT helpdesk ticketing, and dataset evaluation.",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(chat_router)
app.include_router(auth_router)
app.include_router(memory_router)
app.include_router(documents_router)
app.include_router(tickets_router)
app.include_router(datasets_router)
app.include_router(evaluation_router)

@app.on_event("startup")
def on_startup():
    init_db()
    db = SessionLocal()
    try:
        seed_sample_knowledge_base(db)
    finally:
        db.close()

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.project_name,
        "environment": settings.environment,
        "llm_provider": settings.llm_provider
    }

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.app_display_name} API Server",
        "docs_url": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
