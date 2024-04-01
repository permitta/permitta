from sqlalchemy import Integer, Column, String
from .common_mixin_dbo import CommonMixinDbo
from database import BaseModel


class PrincipalDbo(CommonMixinDbo, BaseModel):
    __tablename__ = "principals"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    first_name: str = Column(String)
    last_name: str = Column(String)
    user_name: str = Column(String)
    job_title: str = Column(String)
