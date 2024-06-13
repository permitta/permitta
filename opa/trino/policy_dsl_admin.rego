package permitta.trino

import rego.v1
import data.trino

allow if {
  input_principal_name == "admin"
}