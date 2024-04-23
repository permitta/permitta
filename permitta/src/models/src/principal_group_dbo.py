from dataclasses import dataclass

from database import BaseModel
from sqlalchemy import Column, Integer, String, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, column_property, relationship

from .common_mixin_dbo import IngestionDboMixin


@dataclass
class Attribute:
    attribute_key: str
    attribute_value: str


class PrincipalGroupDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "principal_groups"

    # HACK this is for the UI and should be on a viewmodel
    @property
    def membership_attribute(self) -> Attribute:
        return Attribute(
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
