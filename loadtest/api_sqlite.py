"""Запуск API на SQLite — используется только для локального нагрузочного теста.

В sandbox-окружении (без Docker/PostgreSQL) нужно поднять FastAPI на SQLite.
Скрипт делает monkey-patch UUID-типа PostgreSQL на CHAR(36), переинициализирует
engine и SessionLocal, после чего стартует uvicorn.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ["POSTGRES_HOST"] = "localhost"

from sqlalchemy import create_engine, types
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import sessionmaker

PG_UUID.cache_ok = True


def _load_dialect_impl(self, dialect):
    return dialect.type_descriptor(types.CHAR(36))


def _process_bind_param(self, value, dialect):
    return str(value) if value is not None else None


def _process_result_value(self, value, dialect):
    from uuid import UUID

    return UUID(value) if value is not None else None


PG_UUID.load_dialect_impl = _load_dialect_impl
PG_UUID.process_bind_param = _process_bind_param
PG_UUID.process_result_value = _process_result_value

from app.db import session as session_module

engine = create_engine(
    "sqlite:///./loadtest.db",
    connect_args={"check_same_thread": False},
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

session_module.engine = engine
session_module.SessionLocal = SessionLocal

from app.db.session import Base  # noqa: E402

Base.metadata.create_all(engine)


def _override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from app.main import app  # noqa: E402
from app.db.session import get_db  # noqa: E402

app.dependency_overrides[get_db] = _override_get_db


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")
