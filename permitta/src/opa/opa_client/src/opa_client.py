from dataclasses import asdict

import requests
from app_logger import Logger, get_logger

from .opa_client_config import OpaClientConfig
from .opa_request_model import OpaRequestModel
from .opa_response_model import OpaResponseModel

logger: Logger = get_logger("opa_client")


class OpaClient:
    def __init__(self):
        self.config = OpaClientConfig().load()

    def _get_opa_url(self) -> str:
        return f"{self.config.scheme}://{self.config.hostname}:{self.config.port}{self.config.path}"

    def authorise_request(self, request_method: str) -> bool | None:
        opa_request: OpaRequestModel = OpaRequestModel(
            input={"request_method": request_method}
        )
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
            url=f"{self.config.scheme}://{self.config.hostname}:{self.config.port}/v1/data/permitta/trino/allow",
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
            url=f"{self.config.scheme}://{self.config.hostname}:{self.config.port}/v1/data/permitta/trino/allow",
            opa_request=opa_request,
        )

    def _send_opa_authorize_request(
        self, url: str, opa_request: OpaRequestModel
    ) -> bool | None:
        opa_payload: dict = opa_request.dict()

        try:
            logger.info(f"OPA request: url: {url} payload: {opa_payload}")
            response: requests.Response = requests.post(
                url=url, json=opa_payload, timeout=float(self.config.timeout_seconds)
            )
        except Exception as e:
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
