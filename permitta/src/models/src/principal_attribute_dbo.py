from database import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common_mixin_dbo import IngestionDboMixin


class PrincipalAttributeDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "principal_attributes"

    principal_attribute_id: int = Column(Integer, primary_key=True, autoincrement=True)
    attribute_key: str = Column(String)
    attribute_value: str = Column(String)

    principal_id: Mapped[int] = mapped_column(ForeignKey("principals.principal_id"))
    principal: Mapped["PrincipalDbo"] = relationship(
        back_populates="principal_attributes"
    )

    principal_groups: Mapped[list["PrincipalGroupDbo"]] = relationship(
        "PrincipalGroupDbo",
        primaryjoin="and_(PrincipalAttributeDbo.attribute_key == PrincipalGroupDbo.membership_attribute_key,"
        "PrincipalAttributeDbo.attribute_value == PrincipalGroupDbo.membership_attribute_value)",
        foreign_keys=[attribute_key, attribute_value],
        remote_side="PrincipalGroupDbo.membership_attribute_key, PrincipalGroupDbo.membership_attribute_value",
        uselist=True,
    )
