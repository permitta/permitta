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
        assert policy.policy_id == 1
        session.commit()

    with database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(session=session, policy_id=1)
        assert policy.policy_id == 1
        assert policy.name == "my policy"
        assert policy.description == "A fully sick policy"
