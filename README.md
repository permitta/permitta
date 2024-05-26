# Permitta
Authorise all the things

## Interesting Reading
* https://trino.io/docs/current/security/opa-access-control.html
* https://www.openpolicyagent.org/
* https://www.permit.io/
* https://www.adaltas.com/en/2020/01/22/intro-open-policy-agent-with-kafka/
* https://trino.io/docs/current/develop/system-access-control.html

### Grants:
* https://www.sqlmaestro.com/products/mysql/maestro/help/01_02_02_02_grants/
* https://www.reddit.com/r/snowflake/comments/zlcson/what_are_you_using_to_manage_rolesgrants_in/
* Snowflake only: https://gitlab.com/gitlab-data/permifrost/

## User Stories
### As a data owner
#### Required
* I can quickly identify the objects I am responsible for
* I can see the policies I am responsible for
* I can see the objects and users the policy applies to and how policy changes can affect that
 
#### Stretch
* I can see which users have accessed which objects, when and from what tool
* I can see which users have attempted and failed to access an object
* I can sww which policies have been invoked and by who

### As a data classifier
#### Required
* I can see the objects which are unclassified

#### Stretch
* I can create new classifications
* I can apply and change the classification of objects
* I can be notified when unclassified objects are present, and i can mute these on a per-object/schema basis
* I can see objects for which the classification is disputed

### As a data consumer
#### Required
* I can see what I have access to
* I can see a timeline of how my access changed
* I can see what I don't have access to, and how to get access to it

#### Stretch
* I can request elevated privileges for a limited time 

### As a system administrator
#### Stretch
* Classifications herein can be pushed to downstream platforms (OMD)
* Classifications can be accessed programmatically (API / DB view schema)

### As a CDO
* I have confidence that data owners have full control
* I have confidence that data owners have deep visibility
* I have confidence that data will not be leaked to incorrect users 


## Requirements as per Chris
* Data tags:
  * Domain: Location, RSP Interactions, Customer insights and forecasts
  * Security Label: nbn-COMMERCIAL, nbn-PRIVACY, nbn-RESTRICTED, nbn-PROTECTED
* Roles:
  * Location analyst
  * Location supervisor
  * Field work technician
  * Field work supervisor
  * Payroll analyst
  * Payroll supervisor
  * CPM analyst
  * CPM supervisor
  * All users

* Roles need to be assigned specific tags
* Columns assume the table tags unless replaced (remove?)
* Tags need to be <domain>:<access-rule> :: location:nbn-COMMERCIAL
  
| Role             | Domain                 | Owner | nbn-COMMERCIAL | nbn-PRIVACY | nbn-RESTRICTED | nbn-PROTECTED |
|------------------|------------------------|-------|----------------|-------------|----------------|---------------|
| Location Analyst | Location               |       | X              |             | X              |               |
|                  | Services and assurance |       | X              |             |                |               |
| Location Owner   | Location               | X     |                |             |                |               |

* Policy examples
  * A location analyst can access location commercial and restricted but nothing else
  * Read / Write?


### Questions
* Where do the roles come from? Are they iNow profiles which resolve to AD groups?
  * Do we define the tags associated with the roles?
  * Who can change them and what allows them to do so?
* How are data owners identified and assigned? Manual in UI?
* Does each data object only have one domain? (this is nonsense!)
* Policy complexity:
  * allow when: all principal tags == all object tags
  * deny when: any deny principal tag in all object tags  <-- not quite

## OPA Data Model for ABAC
https://play.openpolicyagent.org/
```jsonc
# input
{
    "data_object": "table_a",
    "principal": "borisyeltsin"
}

# data
{
    "data_objects": {
        "table_a": {
            "location": "commercial"
        }
    },
    "principals": {
        "borisyeltsin": {
            "location": "commercial",
            "customer": "privacy"
        },
        "johnfkennedy": {
            "network": "commercial",
            "location": "commercial"            
        },
        "kevinrudd": {
            "location": "commercial"
        }
    },
    "actions": {
      "read": [ "ShowSchemas", "ExecuteQuery", "FilterSchemas", "SelectFromColumns"] # etc
      "write": ["InsertIntoTable", "DeleteFromTable", "TruncateTable"],
      "ddl": ["AddColumn", "AlterColumn", "DropColumn", "RenameColumn", "CreateView"],
    }
}

# request:
{
  "context": {
    "identity": {
      "user": "foo",
      "groups": ["some-group"]
    },
    "softwareStack": {
      "trinoVersion": "434"
    }
  },
  "action": {
    "operation": "SelectFromColumns",
    "resource": {
      "table": {
        "catalogName": "example_catalog",
        "schemaName": "example_schema",
        "tableName": "example_table",
        "columns": [
          "column1",
          "column2",
          "column3"
        ]
      }
    }
  }
}
```

### Policy
```
package play

import rego.v1

default permit := false
# deny everything by default
default allow := false

# public
permit if {
  "access", "public" in data.data_objects[input.data_object]
  "access", "public" in data.principals[input.principal]    # this line isnt required for public really
}

# RW schema - no DDL
permit if {
  
}

# masked column: GetColumnMask

permit if {
	# evaluates to true if the principal exists in the array
	data.principals[input.principal]
    
	# check the tags on the user match those of the object
	every k, v in data.data_objects[input.data_object] {
    	k, v in data.principals[input.principal]
    }
}

# user cannot see location commercial if they have network commercial
deny if {
	"location", "commercial" in data.data_objects[input.data_object]
    "network", "commercial" in data.principals[input.principal]
}

deny if {
	input.principal == "kevinrudd"
}

# allow if deny is false/undefined and permit is true
allow if {
    permit
    not deny
}



```


## Setup
`venv` and `node_modules` should both be at the project root
```bash
brew install nodejs

brew install python@3.11
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# front end
cd permitta/ui
npm install
npm run build
npm run watch:styles
```

### Environment Variables
| Name                             | Example | Purpose                                       |
|----------------------------------|---------|-----------------------------------------------|
| FLASK_SECRET_KEY                 | <uuid>  | Encrypts the cookies                          |
| OIDC_AUTH_PROVIDER_CLIENT_SECRET |         | The client secret provided by the OIDC server |


### LLDAP
* http://localhost:17170/
* admin / changeme
```bash
# load the users
docker-compose exec lldap /bootstrap/bootstrap.sh
```

## Formatting
```bash
# in project root
isort --profile black permitta/src
black permitta/src
```

## Flask
* Run flask on 8000, or it clashes with airplay
```bash
# nuking a bad flask process
kill $(pgrep -f flask)
```

## Front end
* https://flowbite.com/icons/

## Data Model
* Properties are key-value pairs
* Tags are only values
* Either can be time-bound (from/to)
* Each of the model tables have a staging table

* https://dbdiagram.io/d/permitta-661069f303593b6b61501dd3

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
* OIDC_REDIRECT_URI="http://127.0.0.1:8000/oidccallback"
* Root URL: http://localhost:8000
* Home URL: http://localhost:8000
* Valid redirect URIs: http://127.0.0.1:8000/oidccallback
* Valid post logout redirect URIs: http://127.0.0.1:8000/*
* Web origins: http://localhost:8000/*
* Admin URL: http://localhost:8000

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