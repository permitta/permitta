package httpapi.authz
import input
default allow = false

allow {
#  some username
  input.request_method == "GET"
#  input.request_path = ["users", username]
  input.request_path = ["users"]
#  input.user == username
}

allow {
  input.request_method == "GET"
  input.request_path = ["opa", "policies", "update"]
}