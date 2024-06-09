from database import BaseModel
from models.src.common_mixin_dbo import IngestionDboMixin
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class DatabaseDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "databases"

    database_id = Column(Integer, primary_key=True, autoincrement=True)
    database_name: str = Column(String)

    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.platform_id"))
    platform: Mapped["PlatformDbo"] = relationship(back_populates="databases")

    schemas: Mapped[list["SchemaDbo"]] = relationship(back_populates="database")

    attributes: Mapped[list["DatabaseAttributeDbo"]] = relationship(
        back_populates="database", cascade="all, delete"
    )


class DatabaseAttributeDbo(BaseModel):
    __tablename__ = "database_attributes"

    attribute_id: int = Column(Integer, primary_key=True, autoincrement=True)
    attribute_key: str = Column(String)
    attribute_value: str = Column(String)

    # database FK
    database_id: Mapped[int] = mapped_column(
        ForeignKey("databases.database_id"), nullable=True
    )
    database: Mapped["DatabaseDbo"] = relationship(back_populates="attributes")
