from database import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.src.common_mixin_dbo import IngestionDboMixin


class TableDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "tables"

    table_id = Column(Integer, primary_key=True, autoincrement=True)
    table_name: str = Column(String)

    schema_id: Mapped[int] = mapped_column(ForeignKey("schemas.schema_id"))
    schema: Mapped["SchemaDbo"] = relationship(back_populates="tables")

    columns: Mapped[list["ColumnDbo"]] = relationship(back_populates="table")

    attributes: Mapped[list["ObjectAttributeDbo"]] = relationship(
        back_populates="table", cascade="all, delete"
    )
