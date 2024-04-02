from .database_config import DatabaseConfig
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

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

    def connect(self) -> None:
        database_config: DatabaseConfig = DatabaseConfig.load()
        self.engine: Engine = create_engine(
            database_config.connection_string,
            echo=True,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.Session = sessionmaker(self.engine)
        BaseModel.metadata.create_all(self.engine)

    def disconnect(self) -> None:
        self.engine.dispose()
