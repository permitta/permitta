from database import Database
from models import (
    PrincipalDbo,
    PrincipalGroupDbo,
    PrincipalGroupAttributeDbo,
    PrincipalAttributeDbo,
)
from ..src.principal_repository import PrincipalRepository


def test_get_all(database: Database) -> None:
    repo: PrincipalRepository = PrincipalRepository()

    with database.Session.begin() as session:
        principal_count, principals = repo.get_all(
            session=session,
            sort_col_name="first_name",
            page_number=0,
            page_size=1000000,
        )

        assert principal_count == 198
        assert all([isinstance(p, PrincipalDbo) for p in principals])
        assert len(principals) == 198

        # check sorting
        first_names: list[str] = [p.first_name for p in principals]
        sorted_first_names: list[str] = sorted(first_names)
        assert first_names == sorted_first_names

        # TODO test search with class property


def test_get_all_paginated(database: Database) -> None:
    repo: PrincipalRepository = PrincipalRepository()

    with database.Session.begin() as session:
        principal_count, principals_b1 = repo.get_all(
            session=session, sort_col_name="first_name", page_number=0, page_size=40
        )
        assert principal_count == 198
        assert len(principals_b1) == 40

        principal_count, principals_b2 = repo.get_all(
            session=session, sort_col_name="first_name", page_number=1, page_size=40
        )
        assert principal_count == 198
        assert len(principals_b2) == 40

        principals_b1_ids: list[int] = [p.principal_id for p in principals_b1]
        principals_b2_ids: list[int] = [p.principal_id for p in principals_b2]

        assert not any(
            principals_b1_id in principals_b2_ids
            for principals_b1_id in principals_b1_ids
        )


def test_get_principal_with_attributes(database: Database) -> None:
    repo: PrincipalRepository = PrincipalRepository()

    with database.Session.begin() as session:
        principal: PrincipalDbo = repo.get_principal_with_attributes(
            session=session, principal_id=3
        )
        assert principal.principal_id == 3
        assert principal.first_name == "valtteri"
        assert principal.last_name == "pulkkinen"

        principal_attributes: list = [
            (attr.attribute_key, attr.attribute_value)
            for attr in principal.principal_attributes
        ]

        principal_group_attributes: list = [
            (attr.attribute_key, attr.attribute_value)
            for attr in principal.group_attributes
        ]

        assert principal_attributes == [("ad_group", "MARKETING_ANALYSTS_GL")]
        assert principal_group_attributes == [
            ("Marketing", "Commercial"),
            ("Marketing", "Restricted"),
        ]


def test_get_principal_groups(database: Database) -> None:
    repo: PrincipalRepository = PrincipalRepository()

    with database.Session.begin() as session:
        count, principal_groups = repo.get_principal_groups(
            session=session, sort_col_name="name", page_number=0, page_size=100000
        )
        assert count == 7
        assert all([isinstance(pg, PrincipalGroupDbo) for pg in principal_groups])


def test_get_principal_group_members(database: Database) -> None:
    repo: PrincipalRepository = PrincipalRepository()

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
