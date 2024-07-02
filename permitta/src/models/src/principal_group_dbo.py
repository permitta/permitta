from database import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship

from .common_mixin_dbo import IngestionDboMixin
from .dtos.attribute_dto import AttributeDto


class PrincipalGroupDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "principal_groups"

    # HACK this is for the UI and should be on a viewmodel
    @property
    def membership_attribute(self) -> AttributeDto:
        return AttributeDto(
            attribute_key=self.membership_attribute_key,
            attribute_value=self.membership_attribute_value,
        )

    principal_group_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String())
    description = Column(String())
    membership_attribute_key = Column(String())
    membership_attribute_value = Column(String())

    principal_group_attributes: Mapped[list["PrincipalGroupAttributeDbo"]] = (
        relationship(back_populates="principal_group")
    )
