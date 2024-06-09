from database import BaseModel
from models.src.common_mixin_dbo import IngestionDboMixin
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ColumnDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "columns"

    column_id = Column(Integer, primary_key=True, autoincrement=True)
    column_name: str = Column(String)

    table_id: Mapped[int] = mapped_column(ForeignKey("tables.table_id"))
    table: Mapped["TableDbo"] = relationship(back_populates="columns")

    mask: str = Column(String, server_default="NULL")

    attributes: Mapped[list["ColumnAttributeDbo"]] = relationship(
        back_populates="column", cascade="all, delete"
    )


class ColumnAttributeDbo(BaseModel):
    __tablename__ = "column_attributes"

    attribute_id: int = Column(Integer, primary_key=True, autoincrement=True)
    attribute_key: str = Column(String)
    attribute_value: str = Column(String)

    # column FK
    columntable_id: Mapped[int] = mapped_column(
        ForeignKey("columns.column_id"), nullable=True
    )
    column: Mapped["ColumnDbo"] = relationship(back_populates="attributes")
