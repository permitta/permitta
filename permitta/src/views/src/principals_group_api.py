from typing import Type
from flask import jsonify, render_template
from models import PrincipalDbo
from database import Database
from .view_base import ViewBase


class PrincipalsGroupApi(ViewBase):
    ROUTE_PREFIX = "/principals"

    def get(self):
        # TODO inject this
        database: Database = Database()
        database.connect()

        with database.Session.begin() as session:
            principals: list[Type[PrincipalDbo]] = (
                session.query(PrincipalDbo).limit(20).all()
            )
            principal_count: int = session.query(PrincipalDbo).count()

            return render_template(
                "partials/principals-table-tr.html",
                principals=principals,
                principal_count=principal_count,
            )
