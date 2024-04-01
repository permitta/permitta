import os

from app_config import AppConfigModelBase
from auth import OidcAuthProvider
from flask import Flask, jsonify, render_template, session
from models import PrincipalDbo, sql_alchemy
from views import ApiRegistrar


class FlaskConfig(AppConfigModelBase):
    CONFIG_PREFIX: str = "flask"
    secret_key: str = None


flask_config = FlaskConfig.load()

flask_app = Flask(
    __name__,
    static_url_path="",
    static_folder="../ui/static",
    template_folder="../ui/templates",
)
flask_app.secret_key = flask_config.secret_key


# TODO add this to the oidc thing
flask_app.config.update(OIDC_REDIRECT_URI="http://127.0.0.1:5000/oidccallback")
oidc_auth_provider: OidcAuthProvider = OidcAuthProvider()
oidc_auth_provider.init_app(flask_app=flask_app)

flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///permitta.db"
sql_alchemy.init_app(flask_app)

with flask_app.app_context():
    sql_alchemy.create_all()

    # sql_alchemy.session.add(PrincipalDbo(
    #     first_name="John",
    #     last_name="BonJovi",
    #     user_name="johnbonjovi",
    #     job_title="Vocalist",
    #     tag_name="LDS",
    #     tag_value="Application & Software",
    # ))
    #
    # sql_alchemy.session.add(PrincipalDbo(
    #     first_name="Ritchie",
    #     last_name="Sambora",
    #     user_name="ritchiesambora",
    #     job_title="Axeman",
    #     tag_name="LDS",
    #     tag_value="Fixed Assets",
    # ))
    # sql_alchemy.session.commit()

api_registrar: ApiRegistrar = ApiRegistrar()
api_registrar.init_app(flask_app=flask_app, oidc_auth_provider=oidc_auth_provider)


@flask_app.route("/")
def dashboard():
    return render_template("views/dashboard.html")


@flask_app.route("/policies")
def policies():
    return render_template("views/policies.html")


@flask_app.route("/principals")
def principals():
    return render_template("views/principals.html")


@flask_app.route("/attributes")
@flask_app.route("/")
def attributes():
    return render_template("views/attributes.html")


@flask_app.route("/logout")
@oidc_auth_provider.auth.oidc_logout
def logout():
    return "logged out"
