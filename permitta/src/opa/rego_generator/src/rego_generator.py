import os

import jinja2
from app_logger import Logger, get_logger
from models import PolicyDbo
from repositories import PolicyRepository

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
        logger.info(f"Generating rego document")
        rego_static_content_dir: str = "permitta/src/opa/rego_generator/src/static"
        static_rego_files: list[str] = os.listdir(rego_static_content_dir)

        rego_content: str = ""
        for static_rego_file in static_rego_files:
            static_rego_file_path: str = os.path.join(
                rego_static_content_dir, static_rego_file
            )
            with open(static_rego_file_path) as f:
                logger.info(f"Loaded {static_rego_file_path}")
                rego_content = rego_content + "\n" + f.read()

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
