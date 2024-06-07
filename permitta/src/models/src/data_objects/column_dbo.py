from database import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.src.common_mixin_dbo import IngestionDboMixin


class ColumnDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "columns"

    column_id = Column(Integer, primary_key=True, autoincrement=True)
    column_name: str = Column(String)

    table_id: Mapped[int] = mapped_column(ForeignKey("tables.table_id"))
    table: Mapped["TableDbo"] = relationship(back_populates="columns")

    attributes: Mapped[list["ObjectAttributeDbo"]] = relationship(
        back_populates="column", cascade="all, delete"
    )
