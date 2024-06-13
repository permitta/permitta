import jinja2
from models import PolicyDbo
from repositories import PolicyRepository


class RegoGenerator:
    """
    Rego generator
    Generates a rego snippet from a single policy, or a full rego document by selecting all relevant policies
    """

    @staticmethod
    def generate_snippet_for_policy(policy: PolicyDbo) -> str:
        environment = jinja2.Environment()
        with open("permitta/src/opa/rego_generator/src/snippet_template.rego.j2") as f:
            template = environment.from_string(f.read())
        return template.render(policy=policy)

    @staticmethod
    def generate_rego_document(session) -> str:
        """
        First pass - just directly render the template and return it
        """
        with open("permitta/src/opa/rego_generator/src/common.rego") as f:
            rego_content: str = f.read()

        policies: list[PolicyDbo] = PolicyRepository.get_all(session=session)
        for policy in policies:
            snippet: str = RegoGenerator.generate_snippet_for_policy(policy=policy)
            rego_content += snippet + "\n"

        return rego_content
