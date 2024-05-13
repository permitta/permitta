from models import AttributeDto, DataObjectTableAttributeDbo
from sqlalchemy import Row, and_, or_

from .repository_base import RepositoryBase


class DataObjectRepository(RepositoryBase):

    @staticmethod
    def get_all_unique_attributes(session, search_term: str = "") -> list[AttributeDto]:
        """
        Returns a list of all the unique attributes that a data object can have
        :param session:
        :return:
        """
        attributes: list[DataObjectTableAttributeDbo] = (
            session.query(
                DataObjectTableAttributeDbo.attribute_key,
                DataObjectTableAttributeDbo.attribute_value,
            )
            .distinct()
            .order_by(
                DataObjectTableAttributeDbo.attribute_key,
                DataObjectTableAttributeDbo.attribute_value,
            )
            .filter(
                or_(
                    DataObjectTableAttributeDbo.attribute_key.ilike(f"%{search_term}%"),
                    DataObjectTableAttributeDbo.attribute_value.ilike(
                        f"%{search_term}%"
                    ),
                )
            )
            .all()
        )
        return [
            AttributeDto(attribute_key=a[0], attribute_value=a[1]) for a in attributes
        ]
