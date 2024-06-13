package permitta.trino

import rego.v1
import data.trino

# bob's builder policy
# principal must have principal tags, object must have object tags
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