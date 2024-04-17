import inspect
from typing import Tuple, Type

from database import Database
from models import (
    PrincipalDbo,
    PrincipalGroupDbo,
    PrincipalAttributeDbo,
    PrincipalGroupAttributeDbo,
)

from .repository_base import RepositoryBase
from sqlalchemy.sql.elements import NamedColumn
from sqlalchemy.orm import Query
from sqlalchemy import and_, Row


class PrincipalRepository(RepositoryBase):

    @staticmethod
    def get_all(
        session,
        sort_col_name: str,
        page_number: int,
        page_size: int,
        sort_ascending: bool = True,
        search_term: str = "",
    ) -> Tuple[int, list[PrincipalDbo]]:
        return RepositoryBase.get_all_with_search_and_pagination(
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

    @staticmethod
    def get_principal_groups(
        session,
        sort_col_name: str,
        page_number: int,
        page_size: int,
        sort_ascending: bool = True,
        search_term: str = "",
    ) -> Tuple[int, list[PrincipalGroupDbo]]:
        return RepositoryBase.get_all_with_search_and_pagination(
            model=PrincipalGroupDbo,
            session=session,
            sort_col_name=sort_col_name,
            page_number=page_number,
            page_size=page_size,
            sort_ascending=sort_ascending,
            search_term=search_term,
            search_column_name="name",
        )

    @staticmethod
    def get_principal_group_members(
        session, principal_group_id: int
    ) -> Tuple[int, list[PrincipalDbo]]:
        query: Query = (
            session.query(PrincipalDbo)
            .join(PrincipalAttributeDbo)
            .join(
                PrincipalGroupDbo,
                and_(
                    PrincipalGroupDbo.membership_attribute_key
                    == PrincipalAttributeDbo.attribute_key,
                    PrincipalGroupDbo.membership_attribute_value
                    == PrincipalAttributeDbo.attribute_value,
                ),
            )
            .filter(PrincipalGroupDbo.principal_group_id == principal_group_id)
            .order_by(PrincipalDbo.last_name)
        )
        return query.count(), query.all()
