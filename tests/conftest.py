import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db


@pytest.fixture(autouse=True)
def mock_redis():
    """所有测试自动隔离 Redis，不会真连 localhost:6379"""
    with patch("app.main.redis_client") as mock_redis:
        mock_redis.set.return_value = "OK"
        mock_redis.get.return_value = None
        mock_redis.delete.return_value = 1
        yield mock_redis


@pytest.fixture
def mock_db():
    """用 mock 库会话替换 FastAPI 的真实 get_db 依赖"""
    db = MagicMock()

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield db
    app.dependency_overrides.clear()  # 用完必清，防止污染其他用例


@pytest.fixture
def client(mock_db):
    return TestClient(app)
