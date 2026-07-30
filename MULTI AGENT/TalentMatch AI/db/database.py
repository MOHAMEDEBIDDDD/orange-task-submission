from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from config.settings import settings
from db.models import Base

# Create SQLite engine (supporting multithreaded Streamlit apps)
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all database tables if they do not exist."""
    Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    """Provide a transactional scope around a series of database operations."""
    db: Session = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# Auto-initialize DB on import
init_db()
