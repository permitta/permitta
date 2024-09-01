from typing import Tuple

from app_logger import Logger, get_logger
from auth import OpaAuthzProvider, OpaPermittaAuthzActionEnum
from models import AttributeDto, PolicyDbo
from repositories import PolicyRepository
from views.models import PolicyTRVm

from .principals_controller import PrincipalsController

logger: Logger = get_logger("controllers.policy")


class PoliciesController:
    @staticmethod
    def _get_allowed_policies(
        session, user_name: str, policy: PolicyDbo
    ) -> list[OpaPermittaAuthzActionEnum]:
        principal_attributes: list[AttributeDto] = (
            PrincipalsController.get_principal_attributes_by_username(
                session=session, user_name=user_name
            )
        )
        authz: OpaAuthzProvider = OpaAuthzProvider(
            user_name=user_name,
            user_attributes=principal_attributes,
        )
        return authz.get_allowed_policy_actions(
            object_state=policy.status,
            object_attributes=[],  # TODO filtering by tags
        )

    @staticmethod
    def get_all_with_search_pagination_and_actions(
        session,
        user_name: str,
        sort_col_name: str,
        page_number: int,
        page_size: int,
        search_term: str,
    ) -> Tuple[int, list[PolicyTRVm]]:
        policy_count, policies = PolicyRepository.get_all_with_search_and_pagination(
            session=session,
            sort_col_name=sort_col_name,  # TODO is this SQL injection?
            page_number=page_number,
            page_size=page_size,
            search_term=search_term,
        )

        policy_vms: list[PolicyTRVm] = []
        for policy in policies:
            allowed_actions: list[OpaPermittaAuthzActionEnum] = (
                PoliciesController._get_allowed_policies(
                    session=session, user_name=user_name, policy=policy
                )
            )

            policy_vms.append(
                PolicyTRVm(
                    policy_id=policy.policy_id,
                    name=policy.name,
                    description=policy.description,
                    policy_type=policy.policy_type,
                    author=policy.author,
                    publisher=policy.publisher,
                    status=policy.status,
                    allowed_actions=[a.value for a in allowed_actions],
                )
            )
        return policy_count, policy_vms

    @staticmethod
    def get_policy_with_allowed_actions(
        session, user_name: str, policy_id: int
    ) -> Tuple[PolicyDbo, list[OpaPermittaAuthzActionEnum]]:
        policy: PolicyDbo = PolicyRepository.get_by_id(
            session=session, policy_id=policy_id
        )
        allowed_actions: list[OpaPermittaAuthzActionEnum] = (
            PoliciesController._get_allowed_policies(
                session=session, user_name=user_name, policy=policy
            )
        )
        return policy, allowed_actions
