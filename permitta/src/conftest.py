import os

import pytest
from flask import Flask
from flask.testing import FlaskClient
from pytest_postgresql.janitor import DatabaseJanitor

os.environ["CONFIG_FILE_PATH"] = "permitta/config/config.unittest.yaml"
os.environ["FLASK_SECRET_KEY"] = "dont-tell-anyone"
os.environ["FLASK_TESTING"] = "true"

from app import create_app
from database import Database
from database.src.database_seeder import DatabaseSeeder


@pytest.fixture(scope="module")
def database_empty() -> Database:
    db: Database = Database()
    with DatabaseJanitor(
        user=db.config.user,
        password=db.config.password,
        host=db.config.host,
        port=db.config.port,
        dbname=db.config.database,
        version=16,
        connection_timeout=2,
    ):
        db.connect()
        db.create_all_tables()
        db.create_all_functions()
        yield db


@pytest.fixture(scope="module")
def database(database_empty: Database) -> Database:
    database_seeder: DatabaseSeeder = DatabaseSeeder(db=database_empty)
    database_seeder.seed()
    yield database_empty


@pytest.fixture(scope="module")
def flask_app(database: Database) -> Flask:
    app = create_app(database=database)
    app.config.update(
        {
            "TESTING": True,
        }
    )

    yield app


@pytest.fixture(scope="module")
def client(flask_app: Flask) -> FlaskClient:
    return flask_app.test_client()
