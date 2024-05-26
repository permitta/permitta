import jinja2
from textwrap import dedent
from database import Database
from repositories import PolicyRepository
from models import PolicyDbo, PolicyAttributeDbo


class RegoGenerator:
    """
    Rego generator
    Generates a rego snippet from a single policy, or a full rego document by selecting all relevant policies
    """

    def __init__(self, database: Database):
        self.database = database

    def generate_snippet_for_policy(self, policy_id: int) -> str:
        with self.database.Session.begin() as session:
            policy: PolicyDbo = PolicyRepository.get_by_id(
                session=session, policy_id=policy_id
            )

            if not policy:
                raise ValueError(f"Policy with id {policy_id} was not found")

            # TODO handle direct DSL policies
            if policy.policy_type == PolicyDbo.POLICY_TYPE_BUILDER:
                environment = jinja2.Environment()
                with open("permitta/src/opa/rego_generator/src/snippet_template.rego.j2") as f:
                    template = environment.from_string(f.read())
                return template.render(policy=policy)
            elif policy.policy_type == PolicyDbo.POLICY_TYPE_DSL:
                return policy.policy_dsl
            else:
                raise ValueError(f"Unknown policy type {policy.policy_type}")
