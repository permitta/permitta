## Developer Setup
### Install Dependencies
* `venv` and `node_modules` should both be at the project root
* requires local installation of OPA, python 3.12 and a recent version of nodejs
* supporting apps run under docker-compose
* an SQL client (e.g: dbeaver) is also required

```bash
brew install opa
brew install nodejs
brew install python@3.12

python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# front end
cd permitta/ui
npm install
npm start   # watches both the js folder and tailwind
```

### Formatting
```bash
# in project root
isort --profile black permitta/src
black permitta/src
```
### Running the dev environment
* Run flask on 8000, or it clashes with airplay
* Set the following environment variables

#### Webapp Environment Variables
| Name                             | Purpose                                                                                           |
|----------------------------------|---------------------------------------------------------------------------------------------------|
| FLASK_SECRET_KEY                 | Encrypts the cookies - use a complex, cryptographically secure string                             |
| OIDC_AUTH_PROVIDER_CLIENT_SECRET | The client secret provided by the OIDC server (keycloak) - in docker/keycloak/permitta_realm.json |

```bash
# run dependencies
docker-compose up -d

# populate LLDAP:
docker compose exec lldap /bootstrap/bootstrap.sh

export PYTHONPATH=permitta/src
flask --app permitta.src.app run --debug --port 8000

# nuking a bad flask process
kill $(pgrep -f flask)
```