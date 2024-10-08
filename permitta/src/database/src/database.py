import os

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text

from .database_config import DatabaseConfig

BaseModel = declarative_base()


class Database:
    """
    Usage:

    database: Database = Database()     # no config required
    database.Session.begin() as session:
        session.add(thing)
    # commit is automatic when exiting the with block
    """

    engine: Engine
    Session: sessionmaker
    config: DatabaseConfig

    def __init__(self):
        self.config: DatabaseConfig = DatabaseConfig.load()

    def connect(self) -> None:
        self.engine: Engine = create_engine(
            self.config.connection_string,
            # echo=True,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        self.Session = sessionmaker(self.engine)

    def create_all_tables(self):
        BaseModel.metadata.create_all(self.engine)

    def create_all_functions(self):
        # HACK - this will be replaced by alembic
        with self.Session.begin() as session:
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

    def drop_all_tables(self):
        BaseModel.metadata.drop_all(self.engine)

    def disconnect(self) -> None:
        self.engine.dispose()
