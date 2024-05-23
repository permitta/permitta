from flask.sessions import SessionMixin
from flask_pyoidc.user_session import UserSession


class WebSession:
    _user_session: UserSession

    def __init__(self, flask_session: SessionMixin):
        self._user_session = UserSession(session_storage=flask_session)

    def as_dict(self) -> dict:
        return {
            "given_name": self.given_name,
            "family_name": self.family_name,
            "email": self.email,
        }

    @property
    def is_authenticated(self) -> bool:
        return self._user_session.is_authenticated()

    @property
    def given_name(self) -> str:
        return self._user_session.userinfo.get("given_name")

    @property
    def family_name(self) -> str:
        return self._user_session.userinfo.get("family_name")

    @property
    def full_name(self) -> str:
        return f"{self.given_name.capitalize()} {self.family_name.capitalize()}"

    @property
    def email(self) -> str:
        return self._user_session.userinfo.get("email")

    @property
    def username(self) -> str:
        return self.email.split("@")[0]
