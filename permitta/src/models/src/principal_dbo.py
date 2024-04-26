from database import BaseModel
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, column_property, declared_attr, relationship

from .common_mixin_dbo import IngestionDboMixin


class PrincipalDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "principals"

    @property
    def group_membership_attributes(self) -> list["PrincipalGroupAttributeDbo"]:
        for principal_attribute in self.principal_attributes:
            for principal_group in principal_attribute.principal_groups:
                for (
                    principal_group_attribute
                ) in principal_group.principal_group_attributes:
                    yield principal_group_attribute

    principal_id: int = Column(Integer, primary_key=True, autoincrement=True)
    source_uid: str = Column(String)
    first_name: str = Column(String)
    last_name: str = Column(String)
    user_name: str = Column(String)
    email: str = Column(String)

    principal_attributes: Mapped[list["PrincipalAttributeDbo"]] = relationship(
        back_populates="principal"
    )
