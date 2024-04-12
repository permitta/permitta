from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import declared_attr


class IngestionDboMixin:
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # these cannot be type-hinted or alchemy complains
    process_id = Column(Integer)
    active = Column(Boolean, default=True)
    activated_at = Column(DateTime)
    deactivated_at = Column(DateTime)
