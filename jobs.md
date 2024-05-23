# Jobs

* Trino instance (docker-compose)
 * file based authentication (list of users file) so a user can log in
 * ~20 tables
 * View/table with table names and tags
* Source of user principals with tags / groups (trino, ldap, json)
* Source of group:tag mapping (json)
* Default policy rego
* OPA connected to trino
* INow integration: https://developer.sailpoint.com/docs/api/v3/list-identity-profiles

## Demo sequence
* Log into trino with user, show access
* Change ad group of user, show different access
* Change tags on group, show access change in permitta and matching in dbeaver
* Change policy, show changes in dbeaver/permitta
