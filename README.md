# Permitta
RABAC authorisation for Trino and OPA

## Features
* Web-UI for creating & editing OPA policy documents
  * Drag-and-drop policy editor for basic policies
  * Embedded Rego IDE for complex policies 
* Bundle API for serving data abd policy documents to OPA
* Extensible ingestion framework to acquire tables and users from external sources (e.g trino, ldap)
* Decision log capture / view / search 
* User directory
* Data object catalog
* SSO Integration (OIDC)

## Documentation
https://permitta.github.io/permitta/

## Development
The Permitta dev environment relies on a postgres database, OPA, trino, hive-metastore, minio and lldap to run.
All of these dependencies are present in the `docker-compose` in the repo root

It is recommended to run the dependencies under `docker-compose` and debug the python/js code in your favourite editor 

### Architecture
* Front end is built using HTMX and TailWind CSS, built with `webpack`
* Back end is running flask server to serve both APIs and views
* Unit tests are under `pytest`
* ORM is SQLAlchemy with postgres16, unit tests use `DatabaseJanitor` with dockerised postgres 

### UI API
* Structure is traditional Model-View-Controller
* View models, controllers and views reside under `/views/` (refactor)
* DBO models are returned to template renderer, this is to be refactored to pure view models
* The view module owns the DB session, attained from `flask.g`
* View modules should not directly reference repositories, only via controllers

#### Ingestion
Data ingestion is treated as first-class ETL in Permitta
* Ingestion jobs are asynchronous and CLI-driven. Best deployed using kubernetes CronJobs or similar
* Common ingestion controller instantiates connectors specific to the ingestion source. 
  * Additional sources can easily be added by creating new connectors. Currently supports Trino and LDAP
  * Connectors are python classes based on `ConnectorBase` and yield instances of common ingestion objects
  * Connectors instantiate specific client classes, depending on the use-case. (E.g: LDAP connector instantiates an LDAP client)
* Repository model provides a common `SQL MERGE` tool to provide robust transaction oriented ingestion

### Related Reading
* https://trino.io/docs/current/security/opa-access-control.html
* https://www.openpolicyagent.org/
