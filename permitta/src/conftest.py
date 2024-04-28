import os

import pytest
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy.sql import text

os.environ["CONFIG_FILE_PATH"] = "permitta/config/config.unittest.yaml"
os.environ["SUPER_SECRET_VALUE"] = "dont-tell-anyone"

from database import Database, DatabaseSeeder


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

        # HACK - this will be replaced by alembic
        with db.Session.begin() as session:
            sql_files: list[str] = [
                f
                for f in os.listdir("permitta/src/models/src/functions")
                if f.endswith(".sql")
            ]
            for sql_file in sql_files:
                with open(
                    os.path.join("permitta/src/models/src/functions", sql_file)
                ) as f:
                    session.execute(text(f.read()))

        yield db


@pytest.fixture(scope="module")
def database(database_empty: Database) -> Database:
    database_seeder: DatabaseSeeder = DatabaseSeeder(db=database_empty)
    database_seeder.seed()
    yield database_empty
