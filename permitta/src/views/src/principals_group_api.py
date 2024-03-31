from flask import jsonify, render_template
from models import PrincipalDbo, sql_alchemy

from .view_base import ViewBase


class PrincipalsGroupApi(ViewBase):
    ROUTE_PREFIX = "/principals"

    def get(self):
        principals: list[PrincipalDbo] = sql_alchemy.session.query(PrincipalDbo).all()
        principal_count: int = sql_alchemy.session.query(PrincipalDbo).count()

        return render_template(
            "partials/principals-table-tr.html",
            principals=principals,
            principal_count=principal_count,
        )
