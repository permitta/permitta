package permitta.trino

import rego.v1
import data.trino


all_object_attrs_exist_on_principal if {
  required_principal_attributes := [
    {
      "key": "IT",
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
  principal_has_all_required_attributes(required_principal_attributes)

  # logic:
  # scenario 1: no column level attributes
  #  - permitted object attrs == object attrs

  # scenario 2: column level attribute the user has seperately to this policy
  #  - permitted object attrs == object attrs
  #  - columns will be provided by standard process

  # scenario 3: column level attribute the user does not have
  #  - permitted object attrs == object attrs
  #  - column is masked - provided by standard process

  # scenario 4: column level attribute provided by the policy
  #  - permitted object attrs == object attrs + column attrs
  #  - the sum of the object and column attributes must match
  #  - this must be implemented in the column mask request

  # assert that the object has permitted_object_attributes and no others
  some permitted_object_attribute in permitted_object_attributes
  permitted_object_attribute == data_object_attributes[_]
  count(permitted_object_attributes) == count(data_object_attributes)
}
