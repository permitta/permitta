import responses
from responses import matchers
from ..src.opa_client import OpaClient


@responses.activate
def test_authorise_request():
    responses.add(
        responses.POST,
        "http://localhost:8181/v1/data/permitta/authz",
        match=[matchers.json_params_matcher({"input": {"request_method": "GET"}})],
        json={"result": {"allow": True}},
        status=200,
    )

    responses.add(
        responses.POST,
        "http://localhost:8181/v1/data/permitta/authz",
        match=[matchers.json_params_matcher({"input": {"request_method": "PUT"}})],
        json={"result": {"allow": False}},
        status=200,
    )

    opa_client: OpaClient = OpaClient()

    result_get: bool = opa_client.authorise_request(request_method="GET")
    assert result_get

    result_put: bool = opa_client.authorise_request(request_method="PUT")
    assert not result_put
