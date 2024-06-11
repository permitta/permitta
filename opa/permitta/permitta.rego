package permitta.authz
import input

default allow = false

allow {
  input.request_method == "GET"
}
