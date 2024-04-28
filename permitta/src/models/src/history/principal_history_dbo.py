from datetime import datetime

from database import BaseModel
from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String

from ..common_mixin_dbo import IngestionDboMixin


class PrincipalHistoryDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "principals_history"

    principal_history_id: int = Column(BigInteger, primary_key=True, autoincrement=True)
    changed_at: datetime = Column(DateTime(timezone=True))
    change_operation: str = Column(String)

    principal_id: int = Column(Integer)
    source_uid: str = Column(String)
    first_name: str = Column(String)
    last_name: str = Column(String)
    user_name: str = Column(String)
    email: str = Column(String)
    record_updated_date: str = Column(DateTime(timezone=True))
    record_updated_by: str = Column(String)
