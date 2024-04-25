from database import Database
from models import (
    PrincipalAttributeDbo,
    PrincipalAttributeStagingDbo,
    PrincipalDbo,
    PrincipalGroupAttributeDbo,
    PrincipalGroupDbo,
    PrincipalStagingDbo,
)

from ..src.principal_repository import PrincipalRepository


def test_truncate_staging(database: Database) -> None:
    repo: PrincipalRepository = PrincipalRepository()

    with database.Session.begin() as session:
        session.add(PrincipalStagingDbo())
        session.add(PrincipalAttributeStagingDbo())
        session.commit()

    with database.Session.begin() as session:
        assert session.query(PrincipalStagingDbo).count() == 1
        assert session.query(PrincipalAttributeStagingDbo).count() == 1

        repo.truncate_staging_tables(session=session)
        session.commit()

    with database.Session.begin() as session:
        assert session.query(PrincipalStagingDbo).count() == 0
        assert session.query(PrincipalAttributeStagingDbo).count() == 0


def test_get_all(database: Database) -> None:
    repo: PrincipalRepository = PrincipalRepository()

    with database.Session.begin() as session:
        principal_count, principals = repo.get_all_with_search_and_pagination(
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
        principal_count, principals_b1 = repo.get_all_with_search_and_pagination(
            session=session, sort_col_name="first_name", page_number=0, page_size=40
        )
        assert principal_count == 198
        assert len(principals_b1) == 40

        principal_count, principals_b2 = repo.get_all_with_search_and_pagination(
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

        # test group membership attribute join
        connected_group: PrincipalGroupDbo = (
            principals_b1[0].principal_attributes[0].principal_groups[0]
        )
        assert connected_group.membership_attribute_value == "SALES_SUPERVISORS_GL"
        assert [
            f"{pga.attribute_key}: {pga.attribute_value}"
            for pga in connected_group.principal_group_attributes
        ] == [
            "Sales: Commercial",
            "Sales: Restricted",
            "Sales: Privacy",
            "Marketing: Commercial",
        ]

        # and via the prop on the principal class
        assert [
            f"{pga.attribute_key}: {pga.attribute_value}"
            for pga in principals_b1[0].group_membership_attributes
        ] == [
            "Sales: Commercial",
            "Sales: Restricted",
            "Sales: Privacy",
            "Marketing: Commercial",
        ]


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
