import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(BACKEND))

from app.db.base import Base
from app.db.init_data import init_demo_data
from app.db.session import SessionLocal, engine
from app.models import *  # noqa: F401,F403

Base.metadata.create_all(bind=engine)
db = SessionLocal()
try:
    init_demo_data(db)
finally:
    db.close()

print("Demo data initialized successfully.")
