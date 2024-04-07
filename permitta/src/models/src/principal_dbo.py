from database import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, Mapped
from .common_mixin_dbo import CommonMixinDbo


class PrincipalDbo(CommonMixinDbo, BaseModel):
    __tablename__ = "principals"

    principal_id: int = Column(Integer, primary_key=True, autoincrement=True)
    first_name: str = Column(String)
    last_name: str = Column(String)
    user_name: str = Column(String)
    job_title: str = Column(String)

    principal_attributes: Mapped[list["PrincipalAttributeDbo"]] = relationship(back_populates="principal")
