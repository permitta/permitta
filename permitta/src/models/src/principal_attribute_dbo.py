from database import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .common_mixin_dbo import CommonMixinDbo


class PrincipalAttributeDbo(CommonMixinDbo, BaseModel):
    __tablename__ = "principal_attributes"

    principal_attribute_id: int = Column(Integer, primary_key=True, autoincrement=True)
    attribute_key: str = Column(String)
    attribute_value: str = Column(String)

    principal_id: Mapped[int] = mapped_column(ForeignKey("principals.principal_id"))
    principal: Mapped["PrincipalDbo"] = relationship(back_populates="principal_attributes")