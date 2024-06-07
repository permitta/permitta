from database import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, relationship


class PlatformDbo(BaseModel):
    __tablename__ = "platforms"

    platform_id: int = Column(Integer, primary_key=True, autoincrement=True)
    platform_display_name: str = Column(String)
    platform_type: str = Column(String)

    databases: Mapped[list["DatabaseDbo"]] = relationship(back_populates="platform")

    attributes: Mapped[list["ObjectAttributeDbo"]] = relationship(
        back_populates="platform", cascade="all, delete"
    )
