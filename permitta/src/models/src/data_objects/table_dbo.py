from database import BaseModel
from models.src.common_mixin_dbo import IngestionDboMixin
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class TableDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "tables"

    table_id = Column(Integer, primary_key=True, autoincrement=True)
    table_name: str = Column(String)

    schema_id: Mapped[int] = mapped_column(ForeignKey("schemas.schema_id"))
    schema: Mapped["SchemaDbo"] = relationship(back_populates="tables")

    columns: Mapped[list["ColumnDbo"]] = relationship(back_populates="table")

    attributes: Mapped[list["TableAttributeDbo"]] = relationship(
        back_populates="table", cascade="all, delete"
    )


class TableAttributeDbo(BaseModel):
    __tablename__ = "table_attributes"

    attribute_id: int = Column(Integer, primary_key=True, autoincrement=True)
    attribute_key: str = Column(String)
    attribute_value: str = Column(String)

    # table FK
    table_id: Mapped[int] = mapped_column(ForeignKey("tables.table_id"), nullable=True)
    table: Mapped["TableDbo"] = relationship(back_populates="attributes")
