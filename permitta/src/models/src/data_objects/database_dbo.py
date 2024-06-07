from database import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.src.common_mixin_dbo import IngestionDboMixin


class DatabaseDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "databases"

    database_id = Column(Integer, primary_key=True, autoincrement=True)
    database_name: str = Column(String)

    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.platform_id"))
    platform: Mapped["PlatformDbo"] = relationship(back_populates="databases")

    schemas: Mapped[list["SchemaDbo"]] = relationship(back_populates="database")

    attributes: Mapped[list["ObjectAttributeDbo"]] = relationship(
        back_populates="database", cascade="all, delete"
    )
