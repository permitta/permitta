from extensions import oidc
from flask import Blueprint, render_template

bp = Blueprint("root", __name__, url_prefix="")


@bp.route("/")
@oidc.oidc_auth("default")
def main():
    return render_template("views/main.html")


# @bp.route("/groups")
# @oidc.oidc_auth("default")
# def groups():
#     return render_template("views/groups.html")


# @bp.route("/policies")
# @oidc.oidc_auth("default")
# def policies():
#     return render_template("views/policies.html")


# @bp.route("/principals")
# @oidc.oidc_auth("default")
# def principals():
#     return render_template("views/principals.html")


# @bp.route("/data_objects")
# @oidc.oidc_auth("default")
# def data_objects():
#     return render_template("views/data-objects.html")
