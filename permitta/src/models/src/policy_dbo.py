from datetime import datetime

from database import BaseModel
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import Mapped, column_property, declared_attr, relationship
from sqlalchemy.sql.functions import current_timestamp

from .policy_action_dbo import PolicyActionDbo
from .policy_attribute_dbo import PolicyAttributeDbo


class PolicyDbo(BaseModel):
    __tablename__ = "policies"

    STATUS_PUBLISHED: str = "Published"
    STATUS_DRAFT: str = "Draft"
    STATUS_DISABLED: str = "Disabled"
    STATUS_PENDING_PUBLISH: str = "Pending Publish"
    STATUS_PENDING_DELETE: str = "Pending Delete"

    POLICY_TYPE_BUILDER: str = "Builder"
    POLICY_TYPE_DSL: str = "DSL"

    @property
    def principal_attributes(self):
        return self._filter_attributes_by_type(
            PolicyAttributeDbo.ATTRIBUTE_TYPE_PRINCIPAL
        )

    @property
    def object_attributes(self):
        return self._filter_attributes_by_type(PolicyAttributeDbo.ATTRIBUTE_TYPE_OBJECT)

    def _filter_attributes_by_type(
        self, attribute_type: str
    ) -> list[PolicyAttributeDbo]:
        return [p for p in self.policy_attributes if p.type == attribute_type]

    policy_id: int = Column(Integer, primary_key=True, autoincrement=True)
    policy_type: str = Column(String)
    name: str = Column(String)
    description: str = Column(String)
    status: str = Column(String, server_default=STATUS_DRAFT)
    author: str = Column(String)
    publisher: str = Column(String)

    policy_dsl: str = Column(String)

    record_updated_date: str = Column(
        DateTime(timezone=True), server_default=current_timestamp()
    )
    record_updated_by: str = Column(String)

    policy_attributes: Mapped[list[PolicyAttributeDbo]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )

    policy_actions: Mapped[list[PolicyActionDbo]] = relationship(
        back_populates="policy", cascade="all, delete-orphan"
    )
