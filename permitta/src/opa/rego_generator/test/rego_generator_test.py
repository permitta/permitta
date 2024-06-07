from textwrap import dedent

from database import Database
from models import PolicyDbo
from opa.rego_generator.src.rego_generator import RegoGenerator
from repositories import PolicyRepository


def test_generate_snippet_for_policy(database: Database):
    with database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(session=session, policy_id=3)

        assert dedent(
            RegoGenerator.generate_snippet_for_policy(policy=policy)
        ) == dedent(
            """
            allow if {
                # Policy ID: 3
                # Policy Name: Sales & Marketing Analysts
    
                # Required Principal Attributes
    
                "Sales", "Commercial" in data.principals[input.principal]
    
                # Permitted Object Attributes
    
                "Sales", "Commercial" in data.data_objects[input.data_object]
                "Marketing", "Commercial" in data.data_objects[input.data_object]
            }"""
        )


def test_generate_snippet_for_dsl_policy(database: Database):
    with database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(session=session, policy_id=2)

        assert dedent(
            RegoGenerator.generate_snippet_for_policy(policy=policy)
        ) == dedent(
            """
            allow if {
                # Global Policy
                # All attributes on the object must exist on the principal
                every k, v in data.data_objects[input.data_object] {
                    k, v in data.principals[input.principal]
                }
            }"""
        )
