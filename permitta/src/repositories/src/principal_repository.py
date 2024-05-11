import inspect
from textwrap import dedent
from typing import Tuple, Type

from database import Database
from models import (
    AttributeDto,
    PrincipalAttributeDbo,
    PrincipalAttributeStagingDbo,
    PrincipalDbo,
    PrincipalGroupAttributeDbo,
    PrincipalGroupDbo,
    PrincipalHistoryDbo,
    PrincipalStagingDbo,
)
from sqlalchemy import Row, and_, or_
from sqlalchemy.orm import Query
from sqlalchemy.sql import text
from sqlalchemy.sql.elements import NamedColumn

from .repository_base import RepositoryBase


class PrincipalRepository(RepositoryBase):

    @staticmethod
    def truncate_staging_tables(session) -> None:
        for model in [PrincipalStagingDbo, PrincipalAttributeStagingDbo]:
            session.execute(text(f"truncate {model.__tablename__}"))
            session.execute(
                text(f"alter sequence {model.__tablename__}_id_seq restart with 1")
            )

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
    def get_all_history(session) -> Tuple[int, list[PrincipalHistoryDbo]]:
        query: Query = session.query(PrincipalHistoryDbo)
        return query.count(), query.all()

    @staticmethod
    def get_all_history_by_id(
        session, principal_id: int
    ) -> Tuple[int, list[PrincipalHistoryDbo]]:
        query: Query = session.query(PrincipalHistoryDbo).filter(
            PrincipalHistoryDbo.principal_id == principal_id
        )
        return query.count(), query.all()

    @staticmethod
    def get_by_id(session, principal_id: int) -> PrincipalDbo:
        principal: PrincipalDbo = (
            session.query(PrincipalDbo)
            .filter(PrincipalDbo.principal_id == principal_id)
            .first()
        )
        return principal

    @staticmethod
    def get_all_unique_attribute_kvs(
        session, search_term: str = ""
    ) -> list[AttributeDto]:
        """
        Returns a list of all the unique attributes that a user can have
        :param session:
        :return:
        """
        attributes: list[PrincipalAttributeDbo] = (
            session.query(
                PrincipalAttributeDbo.attribute_key,
                PrincipalAttributeDbo.attribute_value,
            )
            .distinct()
            .union(
                session.query(
                    PrincipalGroupAttributeDbo.attribute_key,
                    PrincipalGroupAttributeDbo.attribute_value,
                ).distinct()
            )
            .order_by(
                PrincipalAttributeDbo.attribute_key,
                PrincipalAttributeDbo.attribute_value,
            )
            .filter(
                or_(
                    PrincipalAttributeDbo.attribute_key.ilike(f"%{search_term}%"),
                    PrincipalAttributeDbo.attribute_value.ilike(f"%{search_term}%"),
                )
            )
            .all()
        )
        return [
            AttributeDto(attribute_key=a[0], attribute_value=a[1]) for a in attributes
        ]

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
    def merge_principals_staging(session, ingestion_process_id: int) -> int:
        merge_stmt: str = PrincipalRepository._get_merge_statement(
            merge_keys=PrincipalStagingDbo.MERGE_KEYS,
            update_cols=PrincipalStagingDbo.UPDATE_COLS,
            ingestion_process_id=ingestion_process_id,
        )
        result = session.execute(text(merge_stmt))
        return result.rowcount

    @staticmethod
    def merge_deactivate_principals_staging(session, ingestion_process_id: int) -> int:
        merge_stmt: str = PrincipalRepository._get_merge_deactivate_statement(
            merge_keys=PrincipalStagingDbo.MERGE_KEYS,
            ingestion_process_id=ingestion_process_id,
        )
        result = session.execute(text(merge_stmt))
        return result.rowcount

    @staticmethod
    def _get_merge_statement(
        merge_keys: list[str], update_cols: list[str], ingestion_process_id: int
    ) -> str:
        merge_key: str = merge_keys[0]  # HACK

        matched_and_stmt: str = "and " + " or ".join(
            [f"src.{c} <> tgt.{c}" for c in update_cols]
        )

        update_stmt: str = (
            "update set "
            + ", ".join([f"{c} = src.{c}" for c in update_cols])
            + f", ingestion_process_id = {ingestion_process_id}"
        )

        insert_stmt: str = (
            "insert ("
            + ", ".join([merge_key] + update_cols)
            + ", ingestion_process_id)"
        )
        values_stmt: str = (
            "values ("
            + ", ".join([f"src.{c}" for c in [merge_key] + update_cols])
            + f", {ingestion_process_id})"
        )

        merge_statement: str = dedent(
            f"""
                    merge into {PrincipalDbo.__tablename__} as tgt
                    using (
                        select * from {PrincipalStagingDbo.__tablename__}
                    ) src
                    on src.{merge_key} = tgt.{merge_key}
                    when matched 
                        {matched_and_stmt}
                    then
                        {update_stmt}
                    when not matched then
                        {insert_stmt}
                        {values_stmt}
                """
        )
        return merge_statement

    @staticmethod
    def _get_merge_deactivate_statement(
        merge_keys: list[str], ingestion_process_id: int
    ) -> str:
        """
        The merge delete statement actually executes an update
        The process ID is set and the record is marked as inactive

        When the trigger proc is called on the update, the function
        should insert a row in the history table with the new proc id
        and delete the record from the target table
        """
        merge_keys_str: str = ", ".join(merge_keys)
        where_clause: str = ", ".join([f"tgt.{c} = src.{c}" for c in merge_keys])

        return dedent(
            f"""
            update {PrincipalDbo.__tablename__} tgt
            set ingestion_process_id = {ingestion_process_id}, active = false
            from (
                select {merge_keys_str} from principals
                except
                select {merge_keys_str} from principals_staging
            ) src
            where {where_clause}
            """
        )
