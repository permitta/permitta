# Policy Management

## Policy States / Workflow
A policy in permitta has an associated state. 
The policy workflow defines which states a policy can move to, depending on its current state

| State           | Description                                              | Possible next states     |
|-----------------|----------------------------------------------------------|--------------------------|
| Draft           | A new policy which currently has no effect               | Pending Publish, Deleted |
| Pending Publish | A policy which is waiting on approval of an owner        | Published, Draft         |
| Published       | A live policy which affects users                        | Pending Disable          |
| Pending Disable | A live policy which is waiting on approval to deactivate | Published, Disables      |
| Disabled        | A policy which was published, but now has no effect      | Deleted, Pending Publish |
| Deleted         | A policy which has been marked deleted                   |                          |

When an owner approves a policy, their relevant attributes are applied to it. 
If they do not have all the required domain ownerships to fully approve the policy, 
then it remains in pending state until another approver has provided the required attribute