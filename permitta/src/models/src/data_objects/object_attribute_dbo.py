from database import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.src.common_mixin_dbo import IngestionDboMixin


class ObjectAttributeDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "object_attributes"

    attribute_id: int = Column(Integer, primary_key=True, autoincrement=True)
    attribute_key: str = Column(String)
    attribute_value: str = Column(String)

    # platform FK
    platform_id: Mapped[int] = mapped_column(
        ForeignKey("platforms.platform_id"), nullable=True
    )
    platform: Mapped["PlatformDbo"] = relationship(back_populates="attributes")

    # database FK
    database_id: Mapped[int] = mapped_column(
        ForeignKey("databases.database_id"), nullable=True
    )
    database: Mapped["DatabaseDbo"] = relationship(back_populates="attributes")

    # schema FK
    schema_id: Mapped[int] = mapped_column(
        ForeignKey("schemas.schema_id"), nullable=True
    )
    schema: Mapped["SchemaDbo"] = relationship(back_populates="attributes")

    # table FK
    table_id: Mapped[int] = mapped_column(ForeignKey("tables.table_id"), nullable=True)
    table: Mapped["TableDbo"] = relationship(back_populates="attributes")

    # column FK
    column_id: Mapped[int] = mapped_column(
        ForeignKey("columns.column_id"), nullable=True
    )
    column: Mapped["ColumnDbo"] = relationship(back_populates="attributes")
