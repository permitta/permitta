from database import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship


class PlatformDbo(BaseModel):
    __tablename__ = "platforms"

    platform_id: int = Column(Integer, primary_key=True, autoincrement=True)
    platform_display_name: str = Column(String)
    platform_type: str = Column(String)

    data_object_tables: Mapped[list["DataObjectTableDbo"]] = relationship(
        back_populates="platform"
    )
