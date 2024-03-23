package httpapi.authz

# HTTP API request
import input

default allow = false

# Allow users to get their own salaries.
allow {
  some username
  input.request_method == "GET"
  input.request_path = ["users", username]
#  input.request_path = ["users"]
#  input.user == username
}

# Allow managers to get their subordinates' salaries.
