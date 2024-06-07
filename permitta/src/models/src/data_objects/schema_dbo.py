from database import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.src.common_mixin_dbo import IngestionDboMixin


class SchemaDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "schemas"

    schema_id = Column(Integer, primary_key=True, autoincrement=True)
    schema_name: str = Column(String)

    database_id: Mapped[int] = mapped_column(ForeignKey("databases.database_id"))
    database: Mapped["DatabaseDbo"] = relationship(back_populates="schemas")

    tables: Mapped[list["TableDbo"]] = relationship(back_populates="schema")

    attributes: Mapped[list["ObjectAttributeDbo"]] = relationship(
        back_populates="schema", cascade="all, delete"
    )
