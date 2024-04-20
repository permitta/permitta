from typing import ClassVar

from database import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, column_property, relationship

from .common_mixin_dbo import IngestionDboMixin


class PrincipalDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "principals"

    principal_id: int = Column(Integer, primary_key=True, autoincrement=True)
    first_name: str = Column(String)
    last_name: str = Column(String)
    user_name: str = Column(String)
    job_title: str = Column(String)

    principal_attributes: Mapped[list["PrincipalAttributeDbo"]] = relationship(
        back_populates="principal"
    )
