import os
import pytest
import importlib
from unittest import mock

@mock.patch.dict(os.environ, {"SECRET_KEY": "testsecret"})
def test_secret_key():
    import cinephoria_backend.config  # Importiere config nach dem Patchen!
    importlib.reload(cinephoria_backend.config)  # Neu laden
    assert cinephoria_backend.config.SECRET_KEY == "testsecret"

@mock.patch.dict(os.environ, {"DATABASE_URL": "postgres://test:test@localhost:5432/test_db"})
def test_database_url():
    import cinephoria_backend.config  # Importiere config nach dem Patchen!
    importlib.reload(cinephoria_backend.config)  # Neu laden
    assert cinephoria_backend.config.DATABASE_URL == "postgres://test:test@localhost:5432/test_db"
