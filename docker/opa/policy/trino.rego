package permitta.trino
import rego.v1

import trino.data

default allow = false

allow if {
	# evaluates to true if the principal exists in the array
	input.context.identity.user in trino.data[principals]

	# check the tags on the user match those of the object
#	every k, v in data.data_objects[input.data_object] {
#    	k, v in data.principals[input.principal]
#    }
}

# Allow batched access
#batch contains i if {
#  some i
#  input.action.filterResources[i]
#  is_admin
#}
# Corner case: filtering columns is done with a single table item, and many columns inside
#batch contains i if {
#  some i
#  input.action.operation == "FilterColumns"
#  count(input.action.filterResources) == 1
#  input.action.filterResources[0].table.columns[i]
#  is_admin
#}
#
#is_admin() if {
#  input.context.identity.user in ["joel","abbas"]
#}