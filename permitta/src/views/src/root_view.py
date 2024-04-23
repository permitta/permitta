from extensions import oidc
from flask import Blueprint, render_template, session as flask_session

bp = Blueprint("root", __name__, url_prefix="")


@bp.route("/")
@oidc.oidc_auth("default")
def main():
    given_name: str = flask_session.get("userinfo").get("given_name")
    family_name: str = flask_session.get("userinfo").get("family_name")
    email: str = flask_session.get("userinfo").get("email")
    return render_template(
        "views/main.html",
        user_full_name=f"{given_name} {family_name}",
        user_email=email,
    )


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
