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

brew install python@3.12
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# front end
cd permitta/ui
npm install
npm start   # watches both the js folder and tailwind
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

opa --help
An open source project to policy-enable your service.

Usage:
  opa [command]

Available Commands:
  bench        Benchmark a Rego query
  build        Build an OPA bundle
  capabilities Print the capabilities of OPA
  check        Check Rego source files
  completion   Generate the autocompletion script for the specified shell
  deps         Analyze Rego query dependencies
  eval         Evaluate a Rego query
  exec         Execute against input files
  fmt          Format Rego source files
  help         Help about any command
  inspect      Inspect OPA bundle(s)
  parse        Parse Rego source file
  run          Start OPA in interactive or server mode
  sign         Generate an OPA bundle signature
  test         Execute Rego test cases
  version      Print the version of OPA

Flags:
  -h, --help   help for opa

Use "opa [command] --help" for more information about a command.

opa run --help
Start an instance of the Open Policy Agent (OPA).

To run the interactive shell:

    $ opa run

To run the server:

    $ opa run -s

The 'run' command starts an instance of the OPA runtime. The OPA runtime can be
started as an interactive shell or a server.

When the runtime is started as a shell, users can define rules and evaluate
expressions interactively. When the runtime is started as a server, OPA exposes
an HTTP API for managing policies, reading and writing data, and executing
queries.

The runtime can be initialized with one or more files that contain policies or
data. If the '--bundle' option is specified the paths will be treated as policy
bundles and loaded following standard bundle conventions. The path can be a
compressed archive file or a directory which will be treated as a bundle.
Without the '--bundle' flag OPA will recursively load ALL rego, JSON, and YAML
files.

When loading from directories, only files with known extensions are considered.
The current set of file extensions that OPA will consider are:

    .json          # JSON data
    .yaml or .yml  # YAML data
    .rego          # Rego file

Non-bundle data file and directory paths can be prefixed with the desired
destination in the data document with the following syntax:

    <dotted-path>:<file-path>

To set a data file as the input document in the interactive shell use the
"repl.input" path prefix with the input file:

    repl.input:<file-path>

Example:

    $ opa run repl.input:input.json

Which will load the "input.json" file at path "data.repl.input".

Use the "help input" command in the interactive shell to see more options.


File paths can be specified as URLs to resolve ambiguity in paths containing colons:

    $ opa run file:///c:/path/to/data.json

URL paths to remote public bundles (http or https) will be parsed as shorthand
configuration equivalent of using repeated --set flags to accomplish the same:

	$ opa run -s https://example.com/bundles/bundle.tar.gz

The above shorthand command is identical to:

    $ opa run -s --set "services.cli1.url=https://example.com" \
                 --set "bundles.cli1.service=cli1" \
                 --set "bundles.cli1.resource=/bundles/bundle.tar.gz" \
                 --set "bundles.cli1.persist=true"

The 'run' command can also verify the signature of a signed bundle.
A signed bundle is a normal OPA bundle that includes a file
named ".signatures.json". For more information on signed bundles
see https://www.openpolicyagent.org/docs/latest/management-bundles/#signing.

The key to verify the signature of signed bundle can be provided
using the --verification-key flag. For example, for RSA family of algorithms,
the command expects a PEM file containing the public key.
For HMAC family of algorithms (eg. HS256), the secret can be provided
using the --verification-key flag.

The --verification-key-id flag can be used to optionally specify a name for the
key provided using the --verification-key flag.

The --signing-alg flag can be used to specify the signing algorithm.
The 'run' command uses RS256 (by default) as the signing algorithm.

The --scope flag can be used to specify the scope to use for
bundle signature verification.

Example:

    $ opa run --verification-key secret --signing-alg HS256 --bundle bundle.tar.gz

The 'run' command will read the bundle "bundle.tar.gz", check the
".signatures.json" file and perform verification using the provided key.
An error will be generated if "bundle.tar.gz" does not contain a ".signatures.json" file.
For more information on the bundle verification process see
https://www.openpolicyagent.org/docs/latest/management-bundles/#signature-verification.

The 'run' command can ONLY be used with the --bundle flag to verify signatures
for existing bundle files or directories following the bundle structure.

To skip bundle verification, use the --skip-verify flag.

The --watch flag can be used to monitor policy and data file-system changes. When a change is detected, the updated policy
and data is reloaded into OPA. Watching individual files (rather than directories) is generally not recommended as some
updates might cause them to be dropped by OPA.

OPA will automatically perform type checking based on a schema inferred from known input documents and report any errors
resulting from the schema check. Currently this check is performed on OPA's Authorization Policy Input document and will
be expanded in the future. To disable this, use the --skip-known-schema-check flag.

The --v1-compatible flag can be used to opt-in to OPA features and behaviors that will be enabled by default in a future OPA v1.0 release.
Current behaviors enabled by this flag include:
- setting OPA's listening address to "localhost:8181" by default.

The --tls-cipher-suites flag can be used to specify the list of enabled TLS 1.0–1.2 cipher suites. Note that TLS 1.3
cipher suites are not configurable. Following are the supported TLS 1.0 - 1.2 cipher suites (IANA):
TLS_RSA_WITH_RC4_128_SHA, TLS_RSA_WITH_3DES_EDE_CBC_SHA, TLS_RSA_WITH_AES_128_CBC_SHA, TLS_RSA_WITH_AES_256_CBC_SHA,
TLS_RSA_WITH_AES_128_CBC_SHA256, TLS_RSA_WITH_AES_128_GCM_SHA256, TLS_RSA_WITH_AES_256_GCM_SHA384, TLS_ECDHE_ECDSA_WITH_RC4_128_SHA,
TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA, TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA, TLS_ECDHE_RSA_WITH_RC4_128_SHA, TLS_ECDHE_RSA_WITH_3DES_EDE_CBC_SHA,
TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA, TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256, TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256,
TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256

See https://godoc.org/crypto/tls#pkg-constants for more information.

Usage:
  opa run [flags] [files]

Flags:
  -a, --addr strings                         set listening address of the server (e.g., [ip]:<port> for TCP, unix://<path> for UNIX domain socket) (default [:8181])
      --authentication {token,tls,off}       set authentication scheme (default off)
      --authorization {basic,off}            set authorization scheme (default off)
  -b, --bundle                               load paths as bundle files or root directories
  -c, --config-file string                   set path of configuration file
      --diagnostic-addr strings              set read-only diagnostic listening address of the server for /health and /metric APIs (e.g., [ip]:<port> for TCP, unix://<path> for UNIX domain socket)
      --disable-telemetry                    disables anonymous information reporting (see: https://www.openpolicyagent.org/docs/latest/privacy)
      --exclude-files-verify strings         set file names to exclude during bundle verification
  -f, --format string                        set shell output format, i.e, pretty, json (default "pretty")
      --h2c                                  enable H2C for HTTP listeners
  -h, --help                                 help for run
  -H, --history string                       set path of history file (default "/.opa_history")
      --ignore strings                       set file and directory names to ignore during loading (e.g., '.*' excludes hidden files)
      --log-format {text,json,json-pretty}   set log format (default json)
  -l, --log-level {debug,info,error}         set log level (default info)
      --log-timestamp-format string          set log timestamp format (OPA_LOG_TIMESTAMP_FORMAT environment variable)
  -m, --max-errors int                       set the number of errors to allow before compilation fails early (default 10)
      --min-tls-version {1.0,1.1,1.2,1.3}    set minimum TLS version to be used by OPA's server (default 1.2)
      --pprof                                enables pprof endpoints
      --ready-timeout int                    wait (in seconds) for configured plugins before starting server (value <= 0 disables ready check)
      --scope string                         scope to use for bundle signature verification
  -s, --server                               start the runtime in server mode
      --set stringArray                      override config values on the command line (use commas to specify multiple values)
      --set-file stringArray                 override config values with files on the command line (use commas to specify multiple values)
      --shutdown-grace-period int            set the time (in seconds) that the server will wait to gracefully shut down (default 10)
      --shutdown-wait-period int             set the time (in seconds) that the server will wait before initiating shutdown
      --signing-alg string                   name of the signing algorithm (default "RS256")
      --skip-known-schema-check              disables type checking on known input schemas
      --skip-verify                          disables bundle signature verification
      --tls-ca-cert-file string              set path of TLS CA cert file
      --tls-cert-file string                 set path of TLS certificate file
      --tls-cert-refresh-period duration     set certificate refresh period
      --tls-cipher-suites strings            set list of enabled TLS 1.0–1.2 cipher suites (IANA)
      --tls-private-key-file string          set path of TLS private key file
      --unix-socket-perm string              specify the permissions for the Unix domain socket if used to listen for incoming connections (default "755")
      --v1-compatible                        opt-in to OPA features and behaviors that will be enabled by default in a future OPA v1.0 release
      --verification-key string              set the secret (HMAC) or path of the PEM file containing the public key (RSA and ECDSA)
      --verification-key-id string           name assigned to the verification key used for bundle verification (default "default")
  -w, --watch                                watch command line files for changes
```