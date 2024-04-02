from typing import Type
from models import PrincipalDbo
from flask import render_template, g, Blueprint, request

bp = Blueprint('principals', __name__, url_prefix='/principals')


@bp.route('/', methods=["GET"])
def principals_table():
    search_term: str = request.args.get('searchTerm', "")

    with g.database.Session.begin() as session:
        principals: list[Type[PrincipalDbo]] = (
            session.query(PrincipalDbo).filter(PrincipalDbo.user_name.ilike(f"%{search_term}%")).limit(20).all()
        )
        principal_count: int = session.query(PrincipalDbo).count()

        return render_template(
            template_name_or_list="partials/principals-table.html",
            principals=principals,
            principal_count=principal_count,
        )

