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
            # Policy ID: 3
            # Policy Name: Sales & Marketing Analysts
            all_object_attrs_exist_on_principal if {
                required_principal_attributes := [
                    {
                      "key": "Sales",
                      "value": "Commercial"
                    }
                ]
                
                permitted_object_attributes := [
                    {
                      "key": "Sales",
                      "value": "Commercial"
                    },
                    {
                      "key": "Marketing",
                      "value": "Commercial"
                    }
                ]
                
                # assert that the principal has all required_principal_attributes
                some required_principal_attribute in required_principal_attributes
                required_principal_attribute == principal_attributes[_]
              
                # assert that the object has permitted_object_attributes and no others
                some permitted_object_attribute in permitted_object_attributes
                permitted_object_attribute == data_object_attributes[_]
                count(permitted_object_attributes) == count(data_object_attributes)
            }
            """
        )


def test_generate_snippet_for_dsl_policy(database: Database):
    with database.Session.begin() as session:
        policy: PolicyDbo = PolicyRepository.get_by_id(session=session, policy_id=2)

        assert dedent(
            RegoGenerator.generate_snippet_for_policy(policy=policy)
        ) == dedent(
            """
            # Policy ID: 2
            # Policy Name: Global ABAC
            
            # global policy - if all object tags are on the principal, then allow
            all_object_attrs_exist_on_principal if {
              # ensure all attrs on object exist on principal
                every data_object_attribute in data_object_attributes {
                some principal_attribute in principal_attributes
                data_object_attribute == principal_attribute
              }
            }
            """
        )


def test_generate_rego_document(database: Database):
    with open("permitta/src/opa/rego_generator/test/trino_test.rego") as f:
        expected: str = f.read()

    with database.Session.begin() as session:
        actual: str = RegoGenerator.generate_rego_document(session=session)
    assert expected == actual
