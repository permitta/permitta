
package httpapi.authz
import input
import data.muckingabout.paths

allow {
  input.request_method == "GET"
  input.request_path = ["users"]
}

allow {
  input.request_method == "GET"
  input.request_path = ["opa", "policies", "update"]
}

allow {
  input.request_method == "GET"
  input.request_path = ["hello"]
}
