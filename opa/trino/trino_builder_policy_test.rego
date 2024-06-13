package permitta.trino

import rego.v1

test_janis_filter_catalog_datalake if {
  allow with input as {
    "action": {
      "operation": "FilterCatalogs",
      "resource": {
        "catalog": {
          "name": "datalake"
        }
      }
    },
    "context": {
      "identity": {
        "user": "janis"
      }
    }
  }
}

test_janis_access_catalog_datalake if {
  allow with input as {
    "action": {
      "operation": "AccessCatalog",
      "resource": {
        "catalog": {
          "name": "datalake"
        }
      }
    },
    "context": {
      "identity": {
        "user": "janis"
      }
    }
  }
}

test_janis_filter_schemas_sales if {
  allow with input as {
    "action": {
      "operation": "FilterSchemas",
      "resource": {
        "schema": {
          "catalogName": "datalake",
          "schemaName": "sales"
        }
      }
    },
    "context": {
      "identity": {
        "user": "janis"
      }
    }
  }
}

test_janis_filter_table if {
  allow with input as {
    "action": {
      "operation": "FilterTables",
      "resource": {
        "table": {
          "catalogName": "datalake",
          "schemaName": "sales",
          "tableName": "customers_markets"
        }
      }
    },
    "context": {
      "identity": {
        "user": "janis"
      }
    }
  }
}

test_janis_filter_columns if {
  allow with input as {
      "action": {
        "operation": "FilterColumns",
        "resource": {
          "table": {
            "catalogName": "datalake",
            "columns": [
              "create_params",
              "type_name"
            ],
            "schemaName": "sales",
            "tableName": "customers_markets"
          }
        }
      },
      "context": {
        "identity": {
          "user": "janis"
        }
      }
    }
}

test_janis_select_from_columns if {
  allow with input as {
      "context": {
          "identity": {
              "user": "janis"
          }
      },
      "action": {
          "operation": "SelectFromColumns",
          "resource": {
              "table": {
                  "catalogName": "datalake",
                  "columns": [
                    "create_params",
                    "type_name"
                  ],
                  "schemaName": "sales",
                  "tableName": "customers_markets"
              }
          }
      }
  }
}

test_janis_column_mask_create_params if {
  not columnmask with input as {
    "action": {
      "operation": "GetColumnMask",
      "resource": {
        "column": {
          "catalogName": "datalake",
          "schemaName": "sales",
          "tableName": "customers_markets",
          "columnName": "create_params",
          "columnType": "varchar"
        }
      }
    },
    "context": {
      "identity": {
        "user": "janis"
      }
    }
  }
}

# not to be implemented for now - too hard
test_janis_column_mask_type_name if {
  not columnmask with input as {
    "action": {
      "operation": "GetColumnMask",
      "resource": {
        "column": {
          "catalogName": "datalake",
          "schemaName": "sales",
          "tableName": "customers_markets",
          "columnName": "type_name",
          "columnType": "varchar"
        }
      }
    },
    "context": {
      "identity": {
        "user": "janis"
      }
    }
  }
}


# policy can provide principal tags and object tags which do not match
# bob doesnt have Marketing:Commercial, so shouldnt work with any other policy
test_allow_bob_builder_policy if {
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
                  "catalogName": "datalake",
                  "schemaName": "sales",
                  "tableName": "customers_markets",
                  "columns": [
                      "create_params",
                      "type_name"
                  ]
              }
          }
      }
  }
}
