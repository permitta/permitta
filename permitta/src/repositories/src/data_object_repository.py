from models import ObjectAttributeDbo
from sqlalchemy import Row, and_, or_

from .repository_base import RepositoryBase


class DataObjectRepository(RepositoryBase):

    @staticmethod
    def get_all_unique_attributes(
        session, search_term: str = ""
    ) -> list[ObjectAttributeDbo]:
        """
        Returns a list of all the unique attributes that a data object can have
        :param session:
        :return:
        """
        attributes: list[ObjectAttributeDbo] = (
            session.query(
                ObjectAttributeDbo.attribute_key,
                ObjectAttributeDbo.attribute_value,
            )
            .distinct()
            .filter(
                or_(
                    ObjectAttributeDbo.attribute_key.ilike(f"%{search_term}%"),
                    ObjectAttributeDbo.attribute_value.ilike(f"%{search_term}%"),
                )
            )
            .order_by(
                ObjectAttributeDbo.attribute_key,
                ObjectAttributeDbo.attribute_value,
            )
            .all()
        )
        return attributes
