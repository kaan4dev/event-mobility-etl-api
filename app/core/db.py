from sqlalcemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.congif import settings

engine = create_engine(settings.db_url, future = True, pool_pre_ping = True)
SessionLocal = sessionmaker(bind = engine, autoflush = False, autocommit = False, future = True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()