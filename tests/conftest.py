# Modern FastAPI testing rule

# Override dependencies, monkeypatch services
# Never run real lifespan logic in unit tests
# tests/conftest.py
# tests/conftest.py (or top of your first test file, before any app imports)
# python -m pytest -v tests
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import pytest
from fastapi.testclient import TestClient
from app.main_rls import create_app
# from app.api.rag import rag_query
from app.config import Settings4Test

class FakeSession:
    pass


@pytest.fixture
def test_app():
    """
    Creates a FastAPI app using TestSettings
    """
    settings = Settings4Test()
    app = create_app(settings)
    return app


@pytest.fixture
def client(test_app):
    """
    Returns a TestClient for the test app
    """
    return TestClient(test_app)
    

@pytest.fixture
def fake_db():
    return FakeSession()


# @pytest.fixture
# def override_db(fake_db):
#     def _get_db():
#         return fake_db

#     rag_query.router.dependency_overrides = {
#         rag_query.fun_get_session: _get_db
#     }

#     yield

#     rag_query.router.dependency_overrides = {}
