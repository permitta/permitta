from opa_client.opa import OpaClient

class PermittaOpaClient:
    client: OpaClient

    def __init__(self):
        self.client = OpaClient(host="localhost", port=8181)  # default host='localhost', port=8181, version='v1'
        self.client.check_connection()  # response is  Yes I'm here :)

    def update_policies(self):
        self.client.update_opa_policy_fromfile(filepath="policy_api/muckingabout.rego", endpoint="fromfile")

    def update_policy_data(self):
        data = ["hello"]
        self.client.update_or_create_opa_data(new_data=data, endpoint="muckingabout/paths")

    def close(self):
        # Ensure the connection is closed correctly by deleting the client
        del self.client