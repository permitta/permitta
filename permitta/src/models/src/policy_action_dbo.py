from database import BaseModel
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import current_timestamp


class PolicyActionDbo(BaseModel):
    __tablename__ = "policy_actions"

    ACTIONS_READ: list[str] = [
        "FilterCatalogs",
        "AccessCatalog",
        "FilterSchemas",
        "FilterTables",
        "FilterColumns",
        "SelectFromColumns",
    ]

    policy_action_id: int = Column(Integer, primary_key=True, autoincrement=True)
    action_name: str = Column(String)

    record_updated_date: str = Column(
        DateTime(timezone=True), server_default=current_timestamp()
    )
    record_updated_by: str = Column(String)

    policy_id: Mapped[int] = mapped_column(ForeignKey("policies.policy_id"))
    policy: Mapped["PolicyDbo"] = relationship(back_populates="policy_actions")
