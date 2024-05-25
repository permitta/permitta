from database import Database
from textwrap import dedent
from opa.rego_generator.src.rego_generator import RegoGenerator


def test_generate_snippet_for_policy(database: Database):
    rego_generator: RegoGenerator = RegoGenerator(database=database)

    assert dedent(rego_generator.generate_snippet_for_policy(1)) == dedent(
        """
        permit if {
            # Policy ID: 1
            # Policy Name: Sales

            # Required Principal Attributes

            "Sales", "Commercial" in data.principals[input.principal]
            "Marketing", "Commercial" in data.principals[input.principal]

            # Permitted Object Attributes

            "Sales", "Commercial" in data.data_objects[input.data_object]
            "Marketing", "Commercial" in data.data_objects[input.data_object]
        }"""
    )