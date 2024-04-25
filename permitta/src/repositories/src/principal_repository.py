import inspect
from typing import Tuple, Type

from database import Database
from models import (
    PrincipalAttributeDbo,
    PrincipalAttributeStagingDbo,
    PrincipalDbo,
    PrincipalGroupAttributeDbo,
    PrincipalGroupDbo,
    PrincipalStagingDbo,
)
from sqlalchemy import Row, and_
from sqlalchemy.orm import Query
from sqlalchemy.sql import text
from sqlalchemy.sql.elements import NamedColumn

from .repository_base import RepositoryBase


class PrincipalRepository(RepositoryBase):

    @staticmethod
    def truncate_staging_tables(session) -> None:
        for model in [PrincipalStagingDbo, PrincipalAttributeStagingDbo]:
            # TODO change this to truncate when we have PG
            session.execute(text(f"delete from {model.__tablename__}"))

    @staticmethod
    def get_all_with_search_and_pagination(
        session,
        sort_col_name: str,
        page_number: int,
        page_size: int,
        sort_ascending: bool = True,
        search_term: str = "",
    ) -> Tuple[int, list[PrincipalDbo]]:
        return RepositoryBase._get_all_with_search_and_pagination(
            model=PrincipalDbo,
            session=session,
            sort_col_name=sort_col_name,
            page_number=page_number,
            page_size=page_size,
            sort_ascending=sort_ascending,
            search_term=search_term,
            search_column_name="user_name",
        )

    @staticmethod
    def get_all(session) -> Tuple[int, list[PrincipalDbo]]:
        query: Query = session.query(PrincipalDbo)
        return query.count(), query.all()

    @staticmethod
    def get_principal_with_attributes(session, principal_id: int) -> PrincipalDbo:
        principal_query: Query = (
            session.query(PrincipalDbo, PrincipalGroupDbo)
            .filter(PrincipalDbo.principal_id == principal_id)
            .join(PrincipalAttributeDbo)
            .join(
                PrincipalGroupDbo,
                and_(
                    PrincipalAttributeDbo.attribute_key
                    == PrincipalGroupDbo.membership_attribute_key,
                    PrincipalAttributeDbo.attribute_value
                    == PrincipalGroupDbo.membership_attribute_value,
                ),
            )
        )
        result: Row = principal_query.first()
        principal: PrincipalDbo = result[0]
        group: PrincipalGroupDbo = result[1]

        # HACK this should really be a dataclass when returned
        principal.group_attributes = group.principal_group_attributes

        return principal
