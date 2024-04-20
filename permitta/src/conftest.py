import os

import pytest

os.environ["CONFIG_FILE_PATH"] = "permitta/config/config.unittest.yaml"
os.environ["SUPER_SECRET_VALUE"] = "dont-tell-anyone"

from database import Database, DatabaseSeeder


@pytest.fixture(scope="module")
def database():
    database_seeder: DatabaseSeeder = DatabaseSeeder()
    database_seeder.seed()
    return database_seeder.db
