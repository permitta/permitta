from dataclasses import asdict, dataclass

import requests
from app_logger import Logger, get_logger

from .opa_authz_provider_config import OpaAuthzProviderConfig

logger: Logger = get_logger("auth.opa")

"""
authorization:
- user can access a particular resource
- requires:
   - the user and associated attributes
   - the resource and associated attributes
   - the action to be taken

Example:
user bob has attrs: domain:customer, ad_group:customer_steward_gl
allowed to edit objects tagged with domain:customer
policy:
 - action in [edit, delete, create]
 - object tagged with domain:customer
 - object type is object
 - user tagged with ad_group:customer_steward_gl
 
 Example:
 all users can see all principals, but not edit
 policy:
  - action in [get]
  - object type is principal
"""


@dataclass
class OpaAttribute:
    key: str
    value: str


@dataclass
class OpaPayload:
    user_name: str
    user_attributes: list[OpaAttribute]
    action: str
    object_type: str
    object_tags: list[OpaAttribute]


class OpaAuthzProvider:
    def __init__(self):
        self.config: OpaAuthzProviderConfig = OpaAuthzProviderConfig().load()

    def authorize(
        self,
        user_name: str,
        user_attributes: list[dict],
        action: str,
        object_type: str,
        object_attributes: list[dict],
    ) -> bool:
        payload: dict = {
            "user_name": user_name,
            "user_attributes": user_attributes,
            "action": action,
            "object_type": object_type,
            "object_attributes": object_attributes,
        }

        response: requests.Response = requests.post(url=self.config.url, json=payload)
        logger.info(
            f"OPA status code:{response.status_code} Body:{response.json()} Text:{response.text}"
        )

        if response.status_code != 200:
            raise Exception(f"Authorisation Error")

        auth_result: dict = response.json()
        return auth_result.get("result", None) is not None
