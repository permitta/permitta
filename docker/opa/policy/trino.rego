package permitta.trino
import rego.v1

default allow = false

# Allow non-batched access
allow if {
  is_admin
}
# Allow batched access
batch contains i if {
  some i
  input.action.filterResources[i]
  is_admin
}
# Corner case: filtering columns is done with a single table item, and many columns inside
batch contains i if {
  some i
  input.action.operation == "FilterColumns"
  count(input.action.filterResources) == 1
  input.action.filterResources[0].table.columns[i]
  is_admin
}

is_admin() if {
  input.context.identity.user in ["joel","abbas"]
}