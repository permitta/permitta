# OIDC Properties

When an OIDC provider (e.g `KeyCloak`, `OKTA`) is configured for permitta, the client properties
the issuer URL, client ID and client secret should be created.

## `oidc_auth_provider.issuer`
* Type: `url`
* Default: `<none>`
* Example: `http://localhost:8080/realms/permitta`

## `oidc_auth_provider.client_id`
* Type: `string`
* Default: `<none>`
* Example: `permitta_client`


## `oidc_auth_provider.client_secret`
* Type: `secret string`
* Default: `<none>`
* Example: `$OIDC_CLIENT_SECRET`


## `oidc_auth_provider.redirect_uri`
* Type: `string`
* Default: `<none>`
* Example: `http://permitta.domain.com/oidccallback`

The `redirect_uri` is the location to which the OIDC service will redirect the
user after a successful login. It should route to `/oidccallback` on Permitta.
