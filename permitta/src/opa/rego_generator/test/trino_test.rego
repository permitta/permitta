package permitta.trino

import rego.v1
import data.trino

data_objects := data.trino.data_objects
principals := data.trino.principals

input_principal_name := input.context.identity.user
action := input.action.operation

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

data_object_is_tagged(data_object) if {
  data_object
  count(data_object.attributes) > 0
}

principal_has_all_required_attributes(required_principal_attributes) if {
  # assert that the principal has all required_principal_attributes
  some required_principal_attribute in required_principal_attributes
  required_principal_attribute == principal_attributes[_]
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

all_classified_column_attrs_exist_on_principal if {
  # for all columns which are in both the input and data
  every classified_column in classified_columns {
    # for every attribute on each of the columns
    every column_attribute in classified_column.attributes {
      # all attrs on the column must be on the principal
      column_attribute == principal_attributes[_]
    }
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
  input.action.operation in ["FilterCatalogs", "AccessCatalog"]
  some data_object in data_objects
	data_object.object.database == input.action.resource.catalog.name
	data_object_is_tagged(data_object)
	all_object_attrs_exist_on_principal
}

# filter schemas - all users see information_schema
allow if {
  input.action.operation == "FilterSchemas"
  input.action.resource.schema.schemaName == "information_schema"
}

allow if {
  input.action.operation == "FilterSchemas"
  some data_object in data_objects
	data_object.object.database == input.action.resource.schema.catalogName
	data_object.object.schema == input.action.resource.schema.schemaName
	data_object_is_tagged(data_object)
	all_object_attrs_exist_on_principal
}

# filter tables
allow if {
  input.action.operation == "FilterTables"
  some data_object in data_objects
	data_object.object == input_table
	data_object_is_tagged(data_object)
	all_object_attrs_exist_on_principal
}

# filter columns - all allowed as masking is default when inaccessible
allow if {
  input.action.operation == "FilterColumns"
#  some data_object in data_objects
#	data_object.object.database == input.action.resource.table.catalogName
#	data_object.object.schema == input.action.resource.table.schemaName
#	data_object.object.table == input.action.resource.table.tableName
#	all_object_attrs_exist_on_principal
#	all_classified_column_attrs_exist_on_principal
}

# running the select
allow if {
  input.action.operation == "SelectFromColumns"
  # ensure we have a valid user
  principal_exists(input_principal_name)

  # ensure the object is tagged
  some data_object in data_objects
	data_object.object == input_table
  data_object_is_tagged(data_object)

  # ensure all attrs on object exist on principal
	all_object_attrs_exist_on_principal
}

# ----------------- column masking rules ---------------------
# the mask value should be applied when a user doesnt have access to it
# when a user doesn't have access, they will still get a true on the column
# if that column doesnt have a defined mask
all_attributes_on_principal(attributes) if {
  every attribute in attributes {
    # all attrs must be on the principal
    attribute == principal_attributes[_]
  }
}

columnmask := {"expression": mask} if {
  some data_object in data_objects
	data_object.object.database == input.action.resource.column.catalogName
	data_object.object.schema == input.action.resource.column.schemaName
	data_object.object.table == input.action.resource.column.tableName

	some column in data_object.columns
	column.name == input.action.resource.column.columnName
	# true if not all attrs on the column are on the principal
	# therefore we should not return a mask
  not all_attributes_on_principal(column.attributes)

  # either return the mask or a default which is null
  mask := object.get(column, "mask", "NULL")
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

#batch contains i if {
#	some i
#	input.action.operation == "FilterColumns"
#	count(input.action.filterResources) == 1
#	raw_resource := input.action.filterResources[0]
#	count(raw_resource.table.columns) > 0
#	new_resources := [
#    object.union(raw_resource, {"table": {"column": column_name}}) | column_name := raw_resource.table.columns[_]
#	]
#	print(new_resources)
#	allow with input.action.resource as new_resources[i]
#}

# Policy ID: 4
# Policy Name: Global ABAC

# global policy - if all object tags are on the principal, then allow
all_object_attrs_exist_on_principal if {
  # ensure all attrs on object exist on principal
    every data_object_attribute in data_object_attributes {
    some principal_attribute in principal_attributes
    data_object_attribute == principal_attribute
  }
}


# Policy ID: 5
# Policy Name: Sales & Marketing Analysts
all_object_attrs_exist_on_principal if {
    required_principal_attributes := [
        {
          "key": "Sales",
          "value": "Commercial"
        }
    ]

    permitted_object_attributes := [
        {
          "key": "Sales",
          "value": "Commercial"
        },
        {
          "key": "Marketing",
          "value": "Commercial"
        }
    ]

    # assert that the principal has all required_principal_attributes
    some required_principal_attribute in required_principal_attributes
    required_principal_attribute == principal_attributes[_]

    # assert that the object has permitted_object_attributes and no others
    some permitted_object_attribute in permitted_object_attributes
    permitted_object_attribute == data_object_attributes[_]
    count(permitted_object_attributes) == count(data_object_attributes)
}

