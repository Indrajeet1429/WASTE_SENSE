from sqlalchemy.orm import sessionmaker

from database.base import engine


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)