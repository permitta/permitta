import uuid
from textwrap import dedent

from models import BaseDbo, PrincipalDbo

from .repository_base import RepositoryBase


class PrincipalRepository(RepositoryBase):
    MODEL: BaseDbo = PrincipalDbo

    def create_temp_table(self) -> str:
        temp_table_name = (
            f"{PrincipalDbo.__tablename__}_{str(uuid.uuid4()).replace('-', '_')}"
        )

        statement: str = dedent(
            f"""
        CREATE TABLE {self.temp_table_name}   
        AS TABLE {PrincipalDbo.__tablename__}
        WITH NO DATA;
        """
        )

        # sql_alchemy.session.execute(statement=statement)
        return temp_table_name
