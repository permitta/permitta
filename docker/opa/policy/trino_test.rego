package permitta.trino

import rego.v1
import data.input.input_filter_cols

test_input_empty if {
  not allow with input as {}
}

test_principal_exists if {
  principal_exists("bob")
}

test_not_principal_exists if {
  not principal_exists("boris")
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
test_access_system_catalog_for_all_users if {
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

# All valid users should have SelectFromColumns on system
test_select_from_system_catalog_for_all_users if {
  allow with input as {
      "context": {
          "identity": {
              "user": "alice"
          }
      },
      "action": {
          "operation": "SelectFromColumns",
          "resource": {
              "table": {
                  "catalogName": "system",
                  "schemaName": "jdbc",
                  "tableName": "types",
                  "columns": [
                      "create_params",
                      "type_name"
                  ]
              }
          }
      }
  }
}

# All valid users should have FilterCatalogs on system
test_select_from_system_catalog_for_all_users if {
  allow with input as {
    "action": {
      "operation": "FilterCatalogs",
      "resource": {
        "catalog": {
          "name": "system"
        }
      }
    },
    "context": {
      "identity": {
        "user": "alice"
      }
    }
  }
}

test_select_from_untagged_table if {
  not allow with input as {
      "context": {
          "identity": {
              "user": "alice"
          }
      },
      "action": {
          "operation": "SelectFromColumns",
          "resource": {
              "table": {
                  "catalogName": "memory",
                  "schemaName": "some_schema",
                  "tableName": "some_table",
                  "columns": [
                      "some_column"
                  ]
              }
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
# filter catalogs should fail for "memory"
test_bob_allow_catalogs if {
  not allow with input as {
    "action": {
      "operation": "FilterCatalogs",
      "resource": {
        "catalog": {
          "name": "memory"
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

# filter catalogs should pass for "iceberg"
test_bob_allow_catalogs if {
  allow with input as {
    "action": {
      "operation": "FilterCatalogs",
      "resource": {
        "catalog": {
          "name": "iceberg"
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

# access catalogs should have the same behaviour as filter catalogs
test_bob_allow_catalogs if {
  not allow with input as {
    "action": {
      "operation": "AccessCatalog",
      "resource": {
        "catalog": {
          "name": "memory"
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

# filter catalogs should pass for "iceberg"
test_bob_allow_catalogs if {
  allow with input as {
    "action": {
      "operation": "AccessCatalog",
      "resource": {
        "catalog": {
          "name": "iceberg"
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

# filter schemas should return hr, logistics and sales
# TODO

# filter tables
test_filter_tables_alice_hr_employees if {
  not allow with input as {
    "action": {
      "operation": "FilterTables",
      "resource": {
        "table": {
          "catalogName": "iceberg",
          "schemaName": "hr",
          "tableName": "employees"
        }
      }
    },
    "context": {
      "identity": {
        "user": "alice"
      }
    }
  }
}

test_filter_tables_alice_logistics_shippers if {
  allow with input as {
    "action": {
      "operation": "FilterTables",
      "resource": {
        "table": {
          "catalogName": "iceberg",
          "schemaName": "logistics",
          "tableName": "shippers"
        }
      }
    },
    "context": {
      "identity": {
        "user": "alice"
      }
    }
  }
}

test_filter_tables_alice_logistics_suppliers if {
  not allow with input as {
    "action": {
      "operation": "FilterTables",
      "resource": {
        "table": {
          "catalogName": "iceberg",
          "schemaName": "logistics",
          "tableName": "suppliers"
        }
      }
    },
    "context": {
      "identity": {
        "user": "alice"
      }
    }
  }
}

# filter columns
test_filter_columns_alice_logistics_regions if {
  allow with input as {
      "action": {
        "operation": "FilterColumns",
        "resource": {
          "table": {
            "catalogName": "iceberg",
            "columns": [
              "column1"
            ],
            "schemaName": "logistics",
            "tableName": "regions"
          }
        }
      },
      "context": {
        "identity": {
          "user": "alice"
        }
      }
    }
}

test_filter_columns_bob_hr_employees_column_a if {
  allow with input as {
      "action": {
        "operation": "FilterColumns",
        "resource": {
          "table": {
            "catalogName": "iceberg",
            "columns": [
              "a"
            ],
            "schemaName": "hr",
            "tableName": "employees"
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

test_filter_columns_bob_hr_employees_column_b if {
  not allow with input as {
      "action": {
        "operation": "FilterColumns",
        "resource": {
          "table": {
            "catalogName": "iceberg",
            "columns": [
              "b"
            ],
            "schemaName": "hr",
            "tableName": "employees"
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
                      "a",
                      "b",
                      "c"
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
                      "a",
                      "b",
                      "c"
                  ]
              }
          }
      }
  }
}

# bob should be able to select column a and column c from hr.employees
test_bob_selects_hr_employees_column_a_and_column_c if {
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
                      "a",
                      "c"
                  ]
              }
          }
      }
  }
}

# bob should not be able to select column b from hr.employees
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
                      "a",
                      "b",
                      "c"
                  ]
              }
          }
      }
  }
}

# frank should be able to select column b from hr.employees
test_frank_selects_hr_employees_all_columns if {
  allow with input as {
    "context": {
        "identity": {
            "user": "frank"
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
                    "a",
                    "b",
                    "c"
                ]
            }
        }
    }
  }
}

# alice should not be able to select column1 and column3 from hr.employees
test_alice_selects_hr_employees_column_a_and_column_c if {
  not allow with input as {
      "context": {
          "identity": {
              "user": "alice"
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
                      "a",
                      "c"
                  ]
              }
          }
      }
  }
}


# classified_columns
test_classified_columns if {
  actual := classified_columns with input as {
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
                    "a",
                    "b",
                    "c"
                ]
            }
        }
    }
  }
  expected := {{"attributes": [{"key": "HR", "value": "Privacy"}], "mask": -1, "name": "b"}}
  actual == expected
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