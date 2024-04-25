from database import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PrincipalAttributeStagingDbo(BaseModel):
    __tablename__ = "principal_attributes_staging"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    principal_source_uid: str = Column(String)
    attribute_key: str = Column(String)
    attribute_value: str = Column(String)
