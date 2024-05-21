from datetime import datetime

from database import BaseModel
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import Mapped, column_property, declared_attr, relationship
from sqlalchemy.sql.functions import current_timestamp


class PolicyDbo(BaseModel):
    __tablename__ = "policies"

    policy_id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String)
    description: str = Column(String)
    enforced_from: datetime = Column(
        DateTime(timezone=True), server_default=current_timestamp()
    )
    enforced_to: datetime = Column(DateTime(timezone=True))

    record_updated_date: str = Column(
        DateTime(timezone=True), server_default=current_timestamp()
    )
    record_updated_by: str = Column(String)

    policy_attributes: Mapped[list["PolicyAttributeDbo"]] = relationship(
        back_populates="policy"
    )
