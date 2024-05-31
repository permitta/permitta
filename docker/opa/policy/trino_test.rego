package permitta.trino

import rego.v1
import data.input.input_select_hr_employees
import data.input.input_select_logistics_territories
import data.input.input_filter_cols

test_input_empty if {
  not allow with input as {}
}

test_user_exists if {
  allow with input as {"context": {"identity": {"user": "joel"}}}
}

test_user_not_exists if {
  not allow with input as {"context": {"identity": {"user": "boris"}}}
}

test_input_select_hr_employees if {
  allow with input as input_select_hr_employees
}

# should fail as the user doesnt have this tag
test_input_select_logistics_territories if {
  not allow with input as input_select_logistics_territories
}

# bob
# filter catalogs should return only iceberg

# filter schemas should return hr, logistics and sales

# ----------------------- insert -----------------------
#import data.input.insert_into_table
#test_input_insert_into_table if {
#  allow with input as insert_into_table
#}

# insert into table i cant acess

# insert into table i have readonly on


#test_input_filter_cols if {
#  batch with input as input_filter_cols
#  print(batch)
#}