from database import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common_mixin_dbo import IngestionDboMixin


class PrincipalGroupAttributeDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "principal_group_attributes"

    principal_group_attribute_id: int = Column(
        Integer, primary_key=True, autoincrement=True
    )
    attribute_key: str = Column(String)
    attribute_value: str = Column(String)

    principal_attribute_id: Mapped[int] = mapped_column(
        ForeignKey("principal_groups.principal_group_id")
    )
    principal_group: Mapped["PrincipalGroupDbo"] = relationship(
        back_populates="principal_group_attributes"
    )
