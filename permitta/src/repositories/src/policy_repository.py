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
    def create(
        session, logged_in_user: str, name: str = "", description: str = ""
    ) -> PolicyDbo:
        policy: PolicyDbo = PolicyDbo(
            name=name,
            description=description,
            record_updated_by=logged_in_user,
            author=logged_in_user,
            policy_type=PolicyDbo.POLICY_TYPE_BUILDER,
        )
        session.add(policy)
        return policy

    @staticmethod
    def clone(
        session,
        policy_id: int,
        logged_in_user: str,
        policy_type: str = PolicyDbo.POLICY_TYPE_BUILDER,
    ) -> PolicyDbo:
        new_policy_dbo: PolicyDbo = PolicyRepository.create(
            session=session, logged_in_user=logged_in_user
        )
        new_policy_dbo.policy_type = policy_type

        source_policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )
        if not source_policy:
            raise ValueError(f"Policy with id {policy_id} does not exist")

        new_policy_dbo.name = source_policy.name
        new_policy_dbo.description = source_policy.description
        new_policy_dbo.author = logged_in_user

        for source_attribute in source_policy.policy_attributes:
            new_policy_attribute_dbo: PolicyAttributeDbo = PolicyAttributeDbo()
            new_policy_attribute_dbo.attribute_key = source_attribute.attribute_key
            new_policy_attribute_dbo.attribute_value = source_attribute.attribute_value
            new_policy_attribute_dbo.type = source_attribute.type
            new_policy_dbo.policy_attributes.append(new_policy_attribute_dbo)

        session.add(new_policy_dbo)
        return new_policy_dbo

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
            search_column_names=["name"],
        )

    @staticmethod
    def get_by_id(session, policy_id: int) -> PolicyDbo:
        policy: PolicyDbo = (
            session.query(PolicyDbo).filter(PolicyDbo.policy_id == policy_id).first()
        )
        return policy

    @staticmethod
    def merge_policy_attributes(
        session, policy_id: int, attribute_type: str, merge_attributes: list[str]
    ) -> None:
        """
        attributes are colon-separated strings

        process:
        get the policy object with attributes
        loop on merge attributes:
          if present in policy, do nothing
          if not present in policy, add
        loop on policy attributes:
          if not present in merge attributes, remove
        """
        policy_attributes: list[PolicyAttributeDbo] = (
            session.query(PolicyAttributeDbo)
            .filter(
                and_(
                    PolicyAttributeDbo.policy_id == policy_id,
                    PolicyAttributeDbo.type == attribute_type,
                )
            )
            .all()
        )
        policy_attribute_strs: list[str] = [
            f"{attr.attribute_key}:{attr.attribute_value}" for attr in policy_attributes
        ]

        # add new attrs
        for merge_attribute in merge_attributes:
            if merge_attribute not in policy_attribute_strs:
                key: str = merge_attribute.split(":")[0]
                value: str = merge_attribute.split(":")[1]

                new_attribute: PolicyAttributeDbo = PolicyAttributeDbo()
                new_attribute.attribute_key = key
                new_attribute.attribute_value = value
                new_attribute.policy_id = policy_id
                new_attribute.type = attribute_type
                session.add(new_attribute)

        # delete removed attrs
        for policy_attribute in policy_attributes:
            if (
                f"{policy_attribute.attribute_key}:{policy_attribute.attribute_value}"
                not in merge_attributes
            ):
                session.delete(policy_attribute)
