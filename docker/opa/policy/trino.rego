package permitta.trino

import rego.v1
import data.trino

data_objects := data.trino.data_objects
principals := data.trino.principals

input_principal_name := input.context.identity.user

input_table := {
	"database": input.action.resource.table.catalogName,
	"schema": input.action.resource.table.schemaName,
	"table": input.action.resource.table.tableName
}

input_columns := input.action.resource.table.columns

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

principal_exists(principal_name) if {
  principal_name
  some principal in principals
  principal.name == principal_name
}

# if columns are specified on the data object, they they have their
# own classification, we need to test them here
# if a column is selected then we need to check it on the object
classified_columns contains classified_column if {
  # get the table from the data
  some data_object in data_objects
	data_object.object == input_table

  # get the set of columns in the input which match the data
  some input_column in input_columns
  input_column == data_object.columns[i].name

  # get the full column object from the data
  some classified_column in data_object.columns
  classified_column.name == input_column
}

all_object_attrs_exist_on_principal if {
  # ensure all attrs on object exist on principal
	every data_object_attribute in data_object_attributes {
    some principal_attribute in principal_attributes
    data_object_attribute == principal_attribute
  }
}

# ExecuteQuery comes with no parameters
allow if {
  # ensure we have a valid user
  input.action.operation == "ExecuteQuery"
  principal_exists(input_principal_name)
}

# All valid users should have AccessCatalog/FilterCatalogs on system
allow if {
  input.action.resource.catalog.name == "system"
  input.action.operation in ["AccessCatalog", "FilterCatalogs"]
  principal_exists(input_principal_name)
}

# All valid users should have SelectFromColumns on system
# TODO replace with catalog tags?
allow if {
  input.action.resource.table.catalogName == "system"
  input.action.operation == "SelectFromColumns"
  principal_exists(input_principal_name)
}

# filter catalogs
# user should have permissions on >0 objects in the target catalog
allow if {
  input.action.operation == "FilterCatalogs"
  some data_object in data_objects
	data_object.object.database == input.action.resource.catalog.name
	all_object_attrs_exist_on_principal
}

# running the select
allow if {
  input.action.operation == "SelectFromColumns"
  # ensure we have a valid user
  principal_exists(input_principal_name)

  # ensure the object is tagged
  count(data_object_attributes) > 0

  # ensure all attrs on object exist on principal
	all_object_attrs_exist_on_principal

  # for all columns which are in both the input and data
  every classified_column in classified_columns {
    # for every attribute on each of the columns
    every column_attribute in classified_column.attributes {
      # all attrs on the column must be on the principal
      column_attribute == principal_attributes
    }
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
