from fastapi import APIRouter

from app.api.agent_tasks import router as tasks_router
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.learning_path import router as path_router
from app.api.tutor import router as tutor_router
from app.api.profile import router as profile_router
from app.api.analytics import router as analytics_router
from app.api.exercises import router as exercises_router
from app.api.knowledge import router as knowledge_router
from app.api.resources import router as resources_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(profile_router)
api_router.include_router(path_router)
api_router.include_router(tasks_router)
api_router.include_router(resources_router)
api_router.include_router(exercises_router)
api_router.include_router(knowledge_router)
api_router.include_router(documents_router)
api_router.include_router(tutor_router)
api_router.include_router(analytics_router)
