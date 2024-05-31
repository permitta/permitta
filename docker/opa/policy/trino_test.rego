package permitta.trino

import rego.v1
import data.input.input_filter_cols

test_input_empty if {
  not allow with input as {}
}

test_user_exists if {
  allow with input as {"context": {"identity": {"user": "bob"}}}
}

test_user_not_exists if {
  not allow with input as {"context": {"identity": {"user": "boris"}}}
}

test_execute_query_permission if {
  allow with input as {
      "context": {
          "identity": {
              "user": "anne"
          }
      },
      "action": {
          "operation": "ExecuteQuery"
      }
  }
}

# All valid users should have AccessCatalog on system
test_access_catalog_for_all_users if {
  allow with input as {
    "action": {
        "operation": "AccessCatalog",
        "resource": {
          "catalog": {
            "name": "system"
          }
        }
      },
      "context": {
        "identity": {
          "user": "bob"
        }
      }
  }
}

# TODO move this to anne
# should fail as the user doesnt have this tag
test_input_select_logistics_territories if {
  not allow with input as {
      "context": {
          "identity": {
              "user": "anne"
          }
      },
      "action": {
          "operation": "SelectFromColumns",
          "resource": {
              "table": {
                  "catalogName": "iceberg",
                  "schemaName": "logistics",
                  "tableName": "territories",
                  "columns": [
                      "column1",
                      "column2",
                      "column3"
                  ]
              }
          }
      }
  }
}

# bob
# filter catalogs should return only iceberg

# filter schemas should return hr, logistics and sales

# bob should be able to select from logistics.shippers, but not logistics.regions
test_bob_selects_logistics_shippers if {
  allow with input as {
      "context": {
          "identity": {
              "user": "bob"
          }
      },
      "action": {
          "operation": "SelectFromColumns",
          "resource": {
              "table": {
                  "catalogName": "iceberg",
                  "schemaName": "logistics",
                  "tableName": "shippers",
                  "columns": [
                      "column1",
                      "column2",
                      "column3"
                  ]
              }
          }
      }
  }
}

test_bob_selects_logistics_regions if {
  not allow with input as {
      "context": {
          "identity": {
              "user": "bob"
          }
      },
      "action": {
          "operation": "SelectFromColumns",
          "resource": {
              "table": {
                  "catalogName": "iceberg",
                  "schemaName": "logistics",
                  "tableName": "regions",
                  "columns": [
                      "column1",
                      "column2",
                      "column3"
                  ]
              }
          }
      }
  }
}

# bob should be able to select column1 and column3 from hr.employees
test_bob_selects_hr_employees_column1_and_column3 if {
  allow with input as {
      "context": {
          "identity": {
              "user": "bob"
          }
      },
      "action": {
          "operation": "SelectFromColumns",
          "resource": {
              "table": {
                  "catalogName": "iceberg",
                  "schemaName": "hr",
                  "tableName": "employees",
                  "columns": [
                      "column1",
                      "column3"
                  ]
              }
          }
      }
  }
}

# bob should not be able to select column2 from hr.employees
test_bob_selects_hr_employees_all_columns if {
  not allow with input as {
      "context": {
          "identity": {
              "user": "bob"
          }
      },
      "action": {
          "operation": "SelectFromColumns",
          "resource": {
              "table": {
                  "catalogName": "iceberg",
                  "schemaName": "hr",
                  "tableName": "employees",
                  "columns": [
                      "column1",
                      "column2",
                      "column3"
                  ]
              }
          }
      }
  }
}

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