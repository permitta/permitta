import jinja2
from models import PolicyDbo


class RegoGenerator:
    """
    Rego generator
    Generates a rego snippet from a single policy, or a full rego document by selecting all relevant policies
    """

    @staticmethod
    def generate_snippet_for_policy(policy: PolicyDbo) -> str:
        if policy.policy_type == PolicyDbo.POLICY_TYPE_BUILDER:
            environment = jinja2.Environment()
            with open(
                "permitta/src/opa/rego_generator/src/snippet_template.rego.j2"
            ) as f:
                template = environment.from_string(f.read())
            return template.render(policy=policy)

        # for DSL type policies
        elif policy.policy_type == PolicyDbo.POLICY_TYPE_DSL:
            return policy.policy_dsl
        else:
            raise ValueError(f"Unknown policy type {policy.policy_type}")

    # @staticmethod
    # def generate_rego_file() -> None:
    #
