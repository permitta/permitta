from textwrap import dedent

from database import Database
from models import (
    PrincipalAttributeDbo,
    PrincipalAttributeStagingDbo,
    PrincipalDbo,
    PrincipalGroupAttributeDbo,
    PrincipalGroupDbo,
    PrincipalHistoryDbo,
    PrincipalStagingDbo,
)

from ..src.principal_repository import PrincipalRepository


def test_merge_principals_staging(database_empty: Database) -> None:
    repo: PrincipalRepository = PrincipalRepository()

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
        assert row_count == 2

        row_count: int = repo.merge_deactivate_principals_staging(
            session=session, ingestion_process_id=2
        )
        assert row_count == 0
        session.commit()

    # test it
    with database_empty.Session.begin() as session:
        count, principals = repo.get_all(session=session)
        assert count == 2
        assert principals[0].principal_id == 1
        assert principals[0].source_uid == "abigail.fleming"
        assert principals[0].ingestion_process_id == 1
        assert principals[0].active
        assert principals[1].principal_id == 2
        assert principals[1].source_uid == "boris.johnstone"
        assert principals[1].ingestion_process_id == 1
        assert principals[1].active

    # scenario 2: append to target tables
    with database_empty.Session.begin() as session:
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
        assert row_count == 1

        row_count: int = repo.merge_deactivate_principals_staging(
            session=session, ingestion_process_id=2
        )
        assert row_count == 0
        session.commit()

    # test it
    with database_empty.Session.begin() as session:
        count, principals = repo.get_all(session=session)
        # one record should be changed
        assert 1 == len([p for p in principals if p.ingestion_process_id == 2])
        assert count == 3

    # scenario 3: update target tables - includes two soft deletes
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
        assert row_count == 1

        row_count: int = repo.merge_deactivate_principals_staging(
            session=session, ingestion_process_id=3
        )
        assert row_count == 2  # two soft deletes
        session.commit()

    # test it
    with database_empty.Session.begin() as session:
        principal: PrincipalDbo = repo.get_by_id(session=session, principal_id=1)
        assert principal.first_name == "Anne"
        assert principal.last_name == "Hathaway"

        count, principals = repo.get_all(session=session)
        # three records should be changed
        assert 3 == len([p for p in principals if p.ingestion_process_id == 3])
        assert 3 == count

        # anne should be active, the others not
        assert repo.get_by_id(session=session, principal_id=1).active
        assert not repo.get_by_id(session=session, principal_id=2).active
        assert not repo.get_by_id(session=session, principal_id=3).active

    #  history tables
    with database_empty.Session.begin() as session:
        count, principal_history = repo.get_all_history(session=session)
        assert 6 == count
        assert 3 == len([p for p in principal_history if p.change_operation == "I"])
        assert 3 == len([p for p in principal_history if p.change_operation == "U"])
        assert 0 == len([p for p in principal_history if p.change_operation == "D"])

        count, ph1 = repo.get_all_history_by_id(session=session, principal_id=1)
        assert 2 == count
        assert ph1[0].change_operation == "I"
        assert ph1[0].first_name == "Abigail"
        assert ph1[1].change_operation == "U"
        assert ph1[1].first_name == "Anne"


def test_get_merge_statement():
    assert (
        dedent(
            """
    merge into principals as tgt
    using (
        select * from principals_staging
    ) src
    on src.source_uid = tgt.source_uid
    when matched 
        and src.first_name <> tgt.first_name or src.last_name <> tgt.last_name or src.user_name <> tgt.user_name or src.email <> tgt.email
    then
        update set first_name = src.first_name, last_name = src.last_name, user_name = src.user_name, email = src.email, ingestion_process_id = 1234
    when not matched then
        insert (source_uid, first_name, last_name, user_name, email, ingestion_process_id)
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
            set ingestion_process_id = 1, active = false
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
