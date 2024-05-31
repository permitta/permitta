package permitta.trino

import rego.v1
import data.trino

data_objects := data.trino.data_objects
principals := data.trino.principals

input_principal_name := input.context.identity.user

input_table := {
	"database": input.action.resource.table.catalogName,
	"schema": input.action.resource.table.schemaName,
	"table": input.action.resource.table.tableName,
}

data_object_attributes contains attribute if {
	some data_object in data_objects
	data_object.object == input_table
	some attribute in data_object.attributes
}

principal_attributes contains attribute if {
  some principal in principals
  principal.name == input_principal_name
  some attribute in principal.attributes
}

principal_exists(input_principal_name) if {
  some principal in principals
  principal.name == input_principal_name
}

allow if {
  # ensure we have a valid user
  input_principal_name
  principal_exists(input_principal_name)

  # ensure all attrs on object exist on principal
  #  print(principal_attributes)
	every data_object_attribute in data_object_attributes {
    some principal_attribute in principal_attributes
    data_object_attribute == principal_attribute
  }
}

# batch mode - run with both the input and output resources if they exist
#batch contains i if {
#	some i
#	raw_resource := input.action.filterResources[i]
#	allow with input.action.resource as raw_resource
#}
#
#data_object_columns contains column if {
##  some i
#	input.action.operation == "FilterColumns"
#	count(input.action.filterResources) == 1
#	raw_resource := input.action.filterResources[0]
#	count(raw_resource.table.columns) > 0
#	new_resources := [
#    object.union(raw_resource, {"table": {"column": column_name}}) | column_name := raw_resource.table.columns[_]
#	]
#	some column in new_resources
#}


batch contains i if {
	some i
	input.action.operation == "FilterColumns"
	count(input.action.filterResources) == 1
	raw_resource := input.action.filterResources[0]
	count(raw_resource.table.columns) > 0
	new_resources := [
    object.union(raw_resource, {"table": {"column": column_name}}) | column_name := raw_resource.table.columns[_]
	]
	print(new_resources)
	allow with input.action.resource as new_resources[i]
}
