from sqlalchemy import create_engine, event, make_url
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .core.config import settings


def normalize_database_url(database_url: str) -> URL:
    url = make_url(database_url)
    if url.get_backend_name() == "postgres":
        return url.set(drivername="postgresql")
    return url


def _set_sqlite_foreign_keys(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_database_engine(database_url: str) -> Engine:
    url = normalize_database_url(database_url)
    is_sqlite = url.get_backend_name() == "sqlite"
    engine = create_engine(
        url,
        connect_args={"check_same_thread": False} if is_sqlite else {},
    )
    if is_sqlite:
        event.listen(engine, "connect", _set_sqlite_foreign_keys)
    return engine


engine = create_database_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    if settings.app_env.lower() != "development":
        return
    from .models import core  # noqa: F401
    Base.metadata.create_all(bind=engine)
