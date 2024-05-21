from datetime import datetime

from database import BaseModel
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import (
    Mapped,
    column_property,
    declared_attr,
    mapped_column,
    relationship,
)
from sqlalchemy.sql.functions import current_timestamp


class PolicyAttributeDbo(BaseModel):
    __tablename__ = "policy_attributes"

    policy_attribute_id: int = Column(Integer, primary_key=True, autoincrement=True)
    key: str = Column(String)
    value: str = Column(String)
    type: str = Column(String)  # principal or object

    record_updated_date: str = Column(
        DateTime(timezone=True), server_default=current_timestamp()
    )
    record_updated_by: str = Column(String)

    policy_id: Mapped[int] = mapped_column(ForeignKey("policies.policy_id"))
    policy: Mapped["PolicyDbo"] = relationship(back_populates="policy_attributes")
