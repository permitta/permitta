# Permitta
Authorise all the things

## Interesting Reading
* https://trino.io/docs/current/security/opa-access-control.html
* https://www.openpolicyagent.org/
* https://www.permit.io/
* https://www.adaltas.com/en/2020/01/22/intro-open-policy-agent-with-kafka/
* https://trino.io/docs/current/develop/system-access-control.html

## Setup
`venv` and `node_modules` should both be at the project root
```bash
brew install nodejs
npm install

brew install python@3.11
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables
| Name                             | Example | Purpose                                       |
|----------------------------------|---------|-----------------------------------------------|
| FLASK_SECRET_KEY                 | <uuid>  | Encrypts the cookies                          |
| OIDC_AUTH_PROVIDER_CLIENT_SECRET |         | The client secret provided by the OIDC server |


## Formatting
```bash
# in project root
isort --profile black permitta/src
black permitta/src
```

## Flask
```bash
# nuking a bad flask process
kill $(pgrep -f flask)
```

## Front end
* https://flowbite.com/icons/

```bash
# tailwind
npm install -D tailwindcss

cd permitta/ui
npx tailwindcss -i ./css/input.css -o ./static/css/output.css --watch
```

## Data Model
* Properties are key-value pairs
* Tags are only values
* Either can be time-bound (from/to)
* Each of the model tables have a staging table


```yaml
ingestion_job_log:
  - process_id
  - job_type
  - source
  - records_retrieved
  - records_ingested
  - records_updated
  - records_deactivated

base:
  - process_id
  - active
  - ingested_at
  - deactivated_at

principal:
  - first_name
  - last_name
  - user_name

property:
  - name
  - value
    
tag: 
  - value

object:
  - platform
  - environment
  - name


```

## Ingestion
### Requirements
* Ingestion jobs are able to run in parallel
* Ingestion jobs can be run on different cadences
* Status / Failures are logged in the DB
* Permission changes are logged to a specific output (splunk etc)
* A bad ingestion job can be undone(!)
* Ingestion jobs can be run in separate pods under K8S CronJobs 

### Process
* Create temporary table
* Load records from source system (e.g. AD / i-now / starburst)
* Merge into main table with source-system filter
  * Insert records missing or deactivated 
  * Deactivate records missing from source
  * Deactivate and insert changed records (all columns are keys?)
  * Ignore unchanged records (leave dates as-is) 


## Run OPA
OPA doesn't automatically update its own policies, it needs a restart
Can be run with `-w` to watch for policy changes
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
tar czf app/static/static/bundles/permitta/bundle.tar.gz policy_bundle

# decision logger
https://gist.github.com/asafc/036ead38d8711e4376a02c98d39877a3

```