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