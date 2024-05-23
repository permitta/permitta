from extensions import oidc
from flask import Blueprint, render_template
from flask import session as flask_session

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
