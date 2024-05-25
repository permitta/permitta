from database import Database
from models import PolicyAttributeDbo, PolicyDbo

from ..src.policy_repository import PolicyRepository


def test_get_by_id(database: Database) -> None:
    # create a policy
    with database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.create(
            session=session,
            name="my policy",
            description="A fully sick policy",
            logged_in_user="homersimpson",
        )
        session.flush()
        policy_id = policy.policy_id
        session.commit()

    with database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )
        assert policy.policy_id == policy_id
        assert policy.name == "my policy"
        assert policy.description == "A fully sick policy"


def test_clone(database: Database) -> None:
    # create a policy
    with database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.create(
            session=session,
            name="my policy",
            description="A fully sick policy",
            logged_in_user="homersimpson",
        )
        policy.policy_attributes = [
            PolicyAttributeDbo(
                attribute_key="attr1",
                attribute_value="val1",
                type=PolicyAttributeDbo.ATTRIBUTE_TYPE_PRINCIPAL,
            ),
            PolicyAttributeDbo(
                attribute_key="attr2",
                attribute_value="val2",
                type=PolicyAttributeDbo.ATTRIBUTE_TYPE_OBJECT,
            ),
        ]

        session.flush()
        original_policy_id = policy.policy_id
        session.commit()

    # clone it
    with database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.clone(
            session=session, policy_id=original_policy_id, logged_in_user="margesimpson"
        )
        session.flush()
        cloned_policy_id = policy.policy_id
        session.commit()

    with database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=cloned_policy_id
        )
        assert policy.policy_id == cloned_policy_id
        assert policy.name == "my policy"
        assert policy.description == "A fully sick policy"
        assert policy.author == "margesimpson"
        assert policy.status == PolicyDbo.STATUS_DRAFT
        assert policy.policy_attributes[0].attribute_key == "attr1"
        assert policy.policy_attributes[0].attribute_value == "val1"
        assert policy.policy_attributes[1].attribute_key == "attr2"
        assert policy.policy_attributes[1].attribute_value == "val2"


def test_merge_policy_attributes(database: Database) -> None:
    # create a policy
    with database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.create(
            session=session,
            name="my policy",
            description="A fully sick policy",
            logged_in_user="homersimpson",
        )
        session.flush()
        policy_id = policy.policy_id
        session.commit()

    # add initial attrs
    initial_policy_attrs: list[str] = [
        "ad_group:MARKETING_ANALYSTS_GL",
        "HR:Commercial",
        "Sales:Marketing",
    ]
    with database.Session.begin() as session:
        PolicyRepository.merge_policy_attributes(
            session=session,
            policy_id=policy_id,
            attribute_type=PolicyAttributeDbo.ATTRIBUTE_TYPE_PRINCIPAL,
            merge_attributes=initial_policy_attrs,
        )
        session.commit()

    policy: PolicyDbo = PolicyRepository.get_by_id(session=session, policy_id=policy_id)
    assert [
        f"{attr.attribute_key}:{attr.attribute_value}"
        for attr in policy.policy_attributes
    ] == initial_policy_attrs

    # add new attrs, remove attrs and change value
    changed_policy_attrs: list[str] = [
        "ad_group:MARKETING_ANALYSTS_GL",  # remain the same
        "HR:Secure",  # change value
        # deleted "Sales:Marketing"
    ]

    with database.Session.begin() as session:
        PolicyRepository.merge_policy_attributes(
            session=session,
            policy_id=policy_id,
            attribute_type=PolicyAttributeDbo.ATTRIBUTE_TYPE_PRINCIPAL,
            merge_attributes=changed_policy_attrs,
        )
        session.commit()

    policy: PolicyDbo = PolicyRepository.get_by_id(session=session, policy_id=policy_id)
    assert [
        f"{attr.attribute_key}:{attr.attribute_value}"
        for attr in policy.policy_attributes
    ] == changed_policy_attrs
