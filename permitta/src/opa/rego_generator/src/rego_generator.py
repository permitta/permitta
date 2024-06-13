import jinja2
from models import PolicyDbo
from repositories import PolicyRepository
from app_logger import Logger, get_logger

logger: Logger = get_logger("opa.bundle_generator")


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
        logger.info(f"Generating rego document")
        common_rego_file_path: str = "permitta/src/opa/rego_generator/src/common.rego"
        with open(common_rego_file_path) as f:
            logger.info(f"Loaded {common_rego_file_path}")
            rego_content: str = f.read()

        policies: list[PolicyDbo] = PolicyRepository.get_all(session=session)
        for policy in policies:
            if policy.status == PolicyDbo.STATUS_PUBLISHED:
                snippet: str = RegoGenerator.generate_snippet_for_policy(policy=policy)
                rego_content += snippet + "\n"
                logger.info(
                    f"Rendered policy ID: {policy.policy_id}, Name: {policy.name}"
                )
            else:
                logger.info(
                    f"Skipped rendering policy ID: {policy.policy_id}, Name: {policy.name}, Status: {policy.status}"
                )

        return rego_content
