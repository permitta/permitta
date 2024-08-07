# Authentication & Authorisation

## Web Authentication
Currently the only available method for authenticating a web user is OIDC. This method should work for all OIDC providers

See [here](../config/configuration.md) for configuration options

## API Authentication
APIs are authenticated using an API key which can be generated via the CLI
See TBA for documentation

## Authorisation
Authorisation within Permitta is governed by OPA (surprise!). A default rego document and policy paradigm is included.
Every HTTP request is authorised, and OPA receives the following payload for each:

```json
{
    "action": "READ",
    "subject": {
        "username": "alice",
        "attributes": [
            {"key": "HR", "value": "Commercial"},
            {"key": "HR", "value": "Privacy"}
        ]
    },
    "object": {
        "type": "POLICY",
        "state": "draft",
        "attributes": [{"key": "IT", "value": "Commercial"}]
    }
}
```
Each payload includes all attributes of the user and the object as well as the action performed. 
Custom rego policies can be supplied to allow very fine-grained and arcane policies to be created, 
according to the specific needs of your organisation.


### Default Authorisation Paradigm
The motivations for the supplied auth-n process are:
* Separation of responsibilities - no one person should be able to make an access change alone
* Delegation - certain individuals are best placed to assign access to specific objects (i.e domain experts)

#### Definitions
**Domain/Subject & Label:** 
Domains or subjects refer to the `key` part of attributes applied to objects or principals
e.g: The attribute `HR:Commercial` has the domain or subject `HR` and the label `Commercial`  


### Default Policies
Permitta ships with a default RABAC policy with the following paradigm

* Read access is granted for all users on all things
* A user with the attribute `permitta_role:admin` has full access to do anything
* Policies for other users are RABAC in the sense that they acquire a role by owning an attribute, but still require other attributes to change certain objects
* Roles are granted via attributes, default attribute names can be updated in the rego, or inherited via attribute groups


#### Roles
| Role Name            | Membership Attribute       | Access Level                                                             |
|----------------------|----------------------------|--------------------------------------------------------------------------|
| Administrator        | `permitta_role:admin`      | All actions on all objects                                               |
| Policy Maintainer    | `permitta_role:maintainer` | Can author all policies dependant on their state                         |
| Domain/Subject Owner | `HR:owner`                 | Can approve the publish or deactivation policies which contain `HR` tags |

##### Policy Maintainer
The role of the policy maintainer is to author policies to provide the specific authorisation requirements.
The maintainer cannot make policy changes which affect users (i.e they cannot publish or deactivate a policy).
Maintainers can request publishing of draft policies, or request deactivation of existing published policies.

##### Domain/Subject Owner
The role of the owner is to approve the publishing of draft policies and deactivation of published policies.
An owner can also be a maintainer, allowing them to author policies as well as approve them, however to provide
separation of responsibilities, no user can approve a policy they have authored. Therefore it is required that
there is at least one owner and one separate maintainer per domain/subject. 

A user can be the owner of multiple domain/subjects, allowing them to approve cross-domain policy changes. 
For more information, see [Policy Management](Policies/policies.md)
























