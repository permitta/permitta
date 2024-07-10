from typing import Tuple

import requests
from app_logger import Logger, get_logger
from opa.models.src.opa_request_model import OpaRequestModel
from opa.models.src.opa_response_model import OpaResponseModel
from pydantic import BaseModel

from .opa_client_config import OpaClientConfig

logger: Logger = get_logger("opa_client")


class OpaClient:
    def __init__(self):
        self.config = OpaClientConfig().load()

    def _get_opa_url(self, path: str | None = None) -> str:
        return f"{self.config.scheme}://{self.config.hostname}:{self.config.port}{path or self.config.path}"

    def put_policy(
        self,
        policy_name: str,
        policy_content: str | None = None,
        policy_file_path: str | None = None,
    ) -> None:
        url: str = self._get_opa_url(path=f"/v1/policies/{policy_name}")

        if policy_file_path:
            with open(policy_file_path) as f:
                policy_content = f.read()

        try:
            logger.info(f"PUT Policy: OPA request: url: {url}")
            response: requests.Response = requests.put(
                url=url, data=policy_content, timeout=float(self.config.timeout_seconds)
            )
            logger.info(
                f"PUT Policy: OPA response: status code: {response.status_code} Body: {response.text}"
            )
        except requests.RequestException as e:
            logger.exception(f"Unexpected error pushing policy to OPA: {e}")

    def authorise_request(self, request_model: BaseModel) -> bool | None:
        opa_request: OpaRequestModel = OpaRequestModel(input=request_model.dict())
        return self._send_opa_authorize_request(
            url=self._get_opa_url(), opa_request=opa_request
        )

    def filter_table(
        self, username: str, database: str, schema: str, table: str
    ) -> bool | None:
        opa_request: OpaRequestModel = OpaRequestModel(
            input={
                "action": {
                    "operation": "FilterTables",
                    "resource": {
                        "table": {
                            "catalogName": database,
                            "schemaName": schema,
                            "tableName": table,
                        }
                    },
                },
                "context": {
                    "identity": {"user": username},
                    "softwareStack": {"permittaVersion": "0.1.0"},
                },
            }
        )
        return self._send_opa_authorize_request(
            url=self._get_opa_url(path="/v1/data/permitta/trino/allow"),
            opa_request=opa_request,
        )

    def filter_schema(self, username: str, database: str, schema: str) -> bool | None:
        opa_request: OpaRequestModel = OpaRequestModel(
            input={
                "action": {
                    "operation": "FilterSchemas",
                    "resource": {
                        "schema": {
                            "catalogName": database,
                            "schemaName": schema,
                        }
                    },
                },
                "context": {
                    "identity": {"user": username},
                    "softwareStack": {"permittaVersion": "0.1.0"},
                },
            }
        )
        return self._send_opa_authorize_request(
            url=self._get_opa_url(path="/v1/data/permitta/trino/allow"),
            opa_request=opa_request,
        )

    def filter_users_with_all_attributes(
        self, username: str, attributes: Tuple[str, str]
    ) -> list[str]:
        pass

    def _send_opa_authorize_request(
        self, url: str, opa_request: OpaRequestModel
    ) -> bool | None:
        opa_payload: dict = opa_request.dict()

        try:
            logger.info(f"OPA request: url: {url} payload: {opa_payload}")
            response: requests.Response = requests.post(
                url=url, json=opa_payload, timeout=float(self.config.timeout_seconds)
            )
        except requests.RequestException as e:
            logger.exception(f"Unexpected error querying OPA: {e}")
            return None

        logger.info(
            f"OPA response: status code: {response.status_code} Json: {response.json()} Body: {response.text}"
        )
        if response.status_code != 200:
            logger.exception(
                f"OPA returned a non-200 status code: {response.status_code}"
            )
            return False

        opa_response: OpaResponseModel = OpaResponseModel(**response.json())
        return opa_response.result
