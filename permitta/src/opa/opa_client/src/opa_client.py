import requests
from dataclasses import asdict
from app_logger import Logger, get_logger
from .opa_request_model import OpaRequestModel, OpaRequestInputModel
from .opa_response_model import OpaResponseModel, OpaResponseAllowModel
from .opa_client_config import OpaClientConfig

logger: Logger = get_logger("opa_client")


class OpaClient:
    def __init__(self):
        self.config = OpaClientConfig().load()

    def _get_opa_url(self) -> str:
        return f"{self.config.scheme}://{self.config.hostname}:{self.config.port}{self.config.path}"

    def authorise_request(self, request_method: str) -> bool:
        opa_request: OpaRequestModel = OpaRequestModel(
            input=OpaRequestInputModel(request_method=request_method)
        )
        opa_url: str = self._get_opa_url()
        opa_payload: dict = opa_request.dict()

        try:
            logger.info(f"OPA request: url: {opa_url} payload: {opa_payload}")
            response: requests.Response = requests.post(url=opa_url, json=opa_payload)
        except Exception as e:
            logger.exception(f"Unexpected error querying OPA: {e}")
            return False

        logger.info(
            f"OPA response: status code: {response.status_code} Json: {response.json()} Body: {response.text}"
        )
        if response.status_code != 200:
            logger.exception(
                f"OPA returned a non-200 status code: {response.status_code}"
            )
            return False

        opa_response: OpaResponseModel = OpaResponseModel(**response.json())
        return opa_response.result.allow
