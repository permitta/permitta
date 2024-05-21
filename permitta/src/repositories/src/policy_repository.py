import inspect
from textwrap import dedent
from typing import Tuple, Type

from database import Database
from models import PolicyAttributeDbo, PolicyDbo
from sqlalchemy import Row, and_, or_
from sqlalchemy.orm import Query
from sqlalchemy.sql import text

from .repository_base import RepositoryBase


class PolicyRepository(RepositoryBase):

    @staticmethod
    def create(session, name: str, description: str, logged_in_user: str) -> PolicyDbo:
        policy: PolicyDbo = PolicyDbo(
            name=name, description=description, record_updated_by=logged_in_user
        )
        session.add(policy)
        return policy

    @staticmethod
    def get_all_with_search_and_pagination(
        session,
        sort_col_name: str,
        page_number: int,
        page_size: int,
        sort_ascending: bool = True,
        search_term: str = "",
    ) -> Tuple[int, list[PolicyDbo]]:
        return RepositoryBase._get_all_with_search_and_pagination(
            model=PolicyDbo,
            session=session,
            sort_col_name=sort_col_name,
            page_number=page_number,
            page_size=page_size,
            sort_ascending=sort_ascending,
            search_term=search_term,
            search_column_name="name",
        )

    @staticmethod
    def get_by_id(session, policy_id: int) -> PolicyDbo:
        policy: PolicyDbo = (
            session.query(PolicyDbo).filter(PolicyDbo.policy_id == policy_id).first()
        )
        return policy
