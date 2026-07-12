import asyncio
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.secret_cipher import SecretCipher, get_secret_cipher
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import User, UserSession  # noqa: F401


@pytest.fixture
def client() -> Iterator[TestClient]:
    database_path = Path(__file__).parent / ".lexis-test.sqlite"
    database_path.unlink(missing_ok=True)
    engine = create_async_engine(
        f"sqlite+aiosqlite:///{database_path.as_posix()}",
        poolclass=NullPool,
    )
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def prepare_database() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    asyncio.run(prepare_database())
    test_cipher = SecretCipher(Fernet.generate_key().decode("utf-8"))
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_secret_cipher] = lambda: test_cipher
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())
    database_path.unlink(missing_ok=True)
