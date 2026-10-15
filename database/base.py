"""SQLAlchemy engine configuration.

For a zero-configuration local demo, SQLite is used when DATABASE_URL is not
provided. Set DATABASE_URL in .env to use PostgreSQL in production/team setups.
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./wastesense.db").strip()
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "").strip()

class Base(DeclarativeBase):
    pass

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
elif DATABASE_PASSWORD and "@" in DATABASE_URL:
    # Support DATABASE_PASSWORD separately without requiring it for SQLite.
    connect_args["password"] = DATABASE_PASSWORD

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
