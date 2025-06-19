from pathlib            import Path
from sqlalchemy         import create_engine
from sqlalchemy.orm     import sessionmaker

DATA_DIR        = Path(__file__).resolve().parent.parent.parent / "data"
DB_PATH         = DATA_DIR / "automobiles.db"
DATABASE_URL    = f"sqlite:///{DB_PATH}"

engine          = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal    = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_engine():
    return engine

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()