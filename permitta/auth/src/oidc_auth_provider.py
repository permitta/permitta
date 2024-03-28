from flask import Flask
from flask_pyoidc.provider_configuration import ProviderConfiguration, ClientMetadata
from flask_pyoidc import OIDCAuthentication


class OidcAuthProvider:
    PROVIDER_NAME: str = "default"
    auth: OIDCAuthentication

    def init_app(self, flask_app: Flask):
        # TODO get from config
        provider_config: ProviderConfiguration = ProviderConfiguration(
            issuer="http://localhost:8080/realms/permitta",
            client_metadata=ClientMetadata(
                client_id="permitta-client", client_secret="AuSlZ8hJoEPcwX6jjTsIx6JXHIYbZLkE"
            ),
        )
        self.auth = OIDCAuthentication({self.PROVIDER_NAME: provider_config})
        self.auth.init_app(flask_app)