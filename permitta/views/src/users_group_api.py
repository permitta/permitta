
from flask import jsonify, render_template
from .view_base import ViewBase
from models import sql_alchemy, PrincipalDbo

class UsersGroupApi(ViewBase):
    ROUTE_PREFIX = "/users"

    def get(self):

        principals: list[PrincipalDbo] = sql_alchemy.session.query(PrincipalDbo).all()
        principal_count: int = sql_alchemy.session.query(PrincipalDbo).count()

        return render_template("partials/users-table-tr.html", principals=principals, principal_count=principal_count)
