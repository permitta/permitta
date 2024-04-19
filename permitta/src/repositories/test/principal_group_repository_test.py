from database import Database
from models import (
    PrincipalDbo,
    PrincipalGroupDbo,
    PrincipalGroupAttributeDbo,
    PrincipalAttributeDbo,
)
from ..src.principal_group_repository import PrincipalGroupRepository


def test_get_all(database: Database) -> None:
    assert False


def test_get_all_paginated(database: Database) -> None:
    assert False


def test_get_principal_groups(database: Database) -> None:
    repo: PrincipalGroupRepository = PrincipalGroupRepository()

    with database.Session.begin() as session:
        count, principal_groups = repo.get_all(
            session=session, sort_col_name="name", page_number=0, page_size=100000
        )
        assert count == 7
        assert all([isinstance(pg, PrincipalGroupDbo) for pg in principal_groups])


def test_get_principal_group_members(database: Database) -> None:
    repo: PrincipalGroupRepository = PrincipalGroupRepository()

    with database.Session.begin() as session:
        count, principal_group_members_batch1 = repo.get_principal_group_members(
            session=session, principal_group_id=1
        )
        assert len(principal_group_members_batch1) == 29
        assert count == 29

        count, principal_group_members_batch2 = repo.get_principal_group_members(
            session=session, principal_group_id=2
        )
        assert not any(
            [
                member in principal_group_members_batch2
                for member in principal_group_members_batch1
            ]
        )
