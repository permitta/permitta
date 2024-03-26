# Permitta
Authorise all the things

## Interesting Reading
* https://trino.io/docs/current/security/opa-access-control.html
* https://www.openpolicyagent.org/
* https://www.permit.io/
* https://www.adaltas.com/en/2020/01/22/intro-open-policy-agent-with-kafka/
* https://trino.io/docs/current/develop/system-access-control.html

## Setup
```bash
brew install python@3.12
python3.12 -m venv venv
source venv/bin/activate
```

## Front End
https://github.com/coreui/coreui-free-bootstrap-admin-template

### Datatables
https://pypi.org/project/django-dynamic-datatb/

```bash
cd app/static
npm install
npm run build
```

## Run OPA
OPA doesn't automatically update its own policies, it needs a restart
```bash
docker-compose up
```

## Keycloak
Settings:
* Realm: permitta
* Client ID: permitta-client
* OIDC_REDIRECT_URI="http://127.0.0.1:5000/oidccallback"
* Root URL: http://localhost:5000
* Home URL: http://localhost:5000
* Valid redirect URIs: http://127.0.0.1:5000/oidccallback
* Valid post logout redirect URIs: http://127.0.0.1:5000/*
* Web origins: http://localhost:5000/*
* Admin URL: http://localhost:5000

Capability Config:
* Client authentication: On
* Authorization: Off
* Authentication flow: Standard Flow

```bash
# https://github.com/busykoala/fastapi-opa/wiki#dev-setup
# https://medium.com/@metacosmos/protect-flask-apis-with-openid-connect-using-flask-pyoidc-3576d9408e46
```

## OPA Stuff
```bash
# tar the bundle folder
tar czf app/static/dist/bundles/permitta/bundle.tar.gz policy_bundle

# decision logger
https://gist.github.com/asafc/036ead38d8711e4376a02c98d39877a3

```