from datetime import datetime

from database import BaseModel
from sqlalchemy import Column, DateTime, Integer, String


class IngestionProcessDbo(BaseModel):
    __tablename__ = "ingestion_processes"

    ingestion_process_id = Column(Integer, primary_key=True, autoincrement=True)
    source = Column(String)  # trino, postgres, ldap etc
    object_type = Column(String)  # tag, object, principal, group
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(String, default="running")
    log = Column(String)
