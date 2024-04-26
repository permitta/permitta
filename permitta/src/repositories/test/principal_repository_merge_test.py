from textwrap import dedent

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


def test_merge_principals_staging(database_empty: Database) -> None:
    repo: PrincipalRepository = PrincipalRepository()

    # TODO add proc id in

    # scenario 1: empty target tables
    with database_empty.Session.begin() as session:
        # populate staging table
        ps1: PrincipalStagingDbo = PrincipalStagingDbo()
        ps1.source_uid = "abigail.fleming"
        ps1.first_name = "Abigail"
        ps1.last_name = "Fleming"
        ps1.user_name = "abigail.fleming"
        ps1.email = "abigail.fleming@mail.com"
        session.add(ps1)

        ps2: PrincipalStagingDbo = PrincipalStagingDbo()
        ps2.source_uid = "boris.johnstone"
        ps2.first_name = "Boris"
        ps2.last_name = "Johnstone"
        ps2.user_name = "boris.johnstone"
        ps2.email = "boris.johnstone@mail.com"
        session.add(ps2)
        session.commit()

    # merge it
    with database_empty.Session.begin() as session:
        row_count: int = repo.merge_principals_staging(
            session=session, ingestion_process_id=1
        )
        session.commit()
        assert row_count == 2

    # test it
    with database_empty.Session.begin() as session:
        count, principals = repo.get_all(session=session)
        assert count == 2
        assert principals[0].principal_id == 1
        assert principals[0].source_uid == "abigail.fleming"
        assert principals[0].process_id == 1
        assert principals[1].principal_id == 2
        assert principals[1].source_uid == "boris.johnstone"
        assert principals[1].process_id == 1

    # scenario 2: append to target tables
    with database_empty.Session.begin() as session:
        # truncate staging table
        repo.truncate_staging_tables(session=session)

        # populate staging table
        ps3: PrincipalStagingDbo = PrincipalStagingDbo()
        ps3.source_uid = "frank.herbert"
        ps3.first_name = "Frank"
        ps3.last_name = "Herbert"
        ps3.user_name = "frank.herbert"
        ps3.email = "frank.herbert@mail.com"
        session.add(ps3)
        session.commit()

    # merge it
    with database_empty.Session.begin() as session:
        row_count: int = repo.merge_principals_staging(
            session=session, ingestion_process_id=2
        )
        session.commit()
        assert row_count == 1

    # test it
    with database_empty.Session.begin() as session:
        count, principals = repo.get_all(session=session)
        # one record should be changed
        assert 1 == len([p for p in principals if p.process_id == 2])
        assert count == 3

    # scenario 3: update target tables
    with database_empty.Session.begin() as session:
        principal: PrincipalDbo = repo.get_by_id(session=session, principal_id=1)
        assert principal.first_name == "Abigail"

        # truncate staging table
        repo.truncate_staging_tables(session=session)

        # populate staging table
        ps: PrincipalStagingDbo = PrincipalStagingDbo()
        ps.source_uid = "abigail.fleming"
        ps.first_name = "Anne"
        ps.last_name = "Hathaway"
        ps.user_name = "abigail.fleming"
        ps.email = "abigail.fleming@mail.com"
        session.add(ps)
        session.commit()

    # merge it
    with database_empty.Session.begin() as session:
        row_count: int = repo.merge_principals_staging(
            session=session, ingestion_process_id=3
        )
        session.commit()
        assert row_count == 1

    # test it
    with database_empty.Session.begin() as session:
        principal: PrincipalDbo = repo.get_by_id(session=session, principal_id=1)
        assert principal.first_name == "Anne"
        assert principal.last_name == "Hathaway"

        count, principals = repo.get_all(session=session)
        # one record should be changed
        assert 1 == len([p for p in principals if p.process_id == 3])
        assert 3 == count

    # scenario 3: delete from target tables

    # extra for experts: history tables
    assert False


def test_get_merge_statement():
    assert (
        dedent(
            """
    merge into principals as tgt
    using (
        select * from principals_staging
    ) src
    on src.source_uid = tgt.source_uid
    when matched then
        update set first_name = src.first_name, last_name = src.last_name, user_name = src.user_name, email = src.email, process_id = 1234
    when not matched then
        insert (source_uid, first_name, last_name, user_name, email, process_id)
        values (src.source_uid, src.first_name, src.last_name, src.user_name, src.email, 1234)
    """
        )
        == PrincipalRepository._get_merge_statement(
            merge_keys=["source_uid"],
            update_cols=["first_name", "last_name", "user_name", "email"],
            ingestion_process_id=1234,
        )
    )


def test_get_merge_deactivate_statement():
    assert (
        dedent(
            """
            update principals tgt
            set process_id = 1, active = false
            from (
                select source_uid, id from principals
                except
                select source_uid, id from principals_staging
            ) src
            where tgt.source_uid = src.source_uid, tgt.id = src.id
        """
        )
        == PrincipalRepository._get_merge_deactivate_statement(
            merge_keys=["source_uid", "id"], ingestion_process_id=1
        )
    )
