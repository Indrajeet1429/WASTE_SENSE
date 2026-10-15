from collections.abc import Generator

from sqlalchemy.orm import Session

from database.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Provide one database session per request."""
    db = SessionLocal()

    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
