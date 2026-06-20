from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    import app.db.session as sess
    from app.db.base import Base
    import app.models  # noqa: F401  — registers all models with Base
    from app.db.init_data import init_demo_data

    Base.metadata.create_all(bind=sess.engine)
    db = sess.SessionLocal()
    try:
        init_demo_data(db)
    finally:
        db.close()
    yield


app = FastAPI(title="EduPath Agent", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}
