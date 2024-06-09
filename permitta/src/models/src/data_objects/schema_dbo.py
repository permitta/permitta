from database import BaseModel
from models.src.common_mixin_dbo import IngestionDboMixin
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class SchemaDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "schemas"

    schema_id = Column(Integer, primary_key=True, autoincrement=True)
    schema_name: str = Column(String)

    database_id: Mapped[int] = mapped_column(ForeignKey("databases.database_id"))
    database: Mapped["DatabaseDbo"] = relationship(back_populates="schemas")

    tables: Mapped[list["TableDbo"]] = relationship(back_populates="schema")

    attributes: Mapped[list["SchemaAttributeDbo"]] = relationship(
        back_populates="schema", cascade="all, delete"
    )


class SchemaAttributeDbo(BaseModel):
    __tablename__ = "schema_attributes"

    attribute_id: int = Column(Integer, primary_key=True, autoincrement=True)
    attribute_key: str = Column(String)
    attribute_value: str = Column(String)

    # schema FK
    schema_id: Mapped[int] = mapped_column(
        ForeignKey("schemas.schema_id"), nullable=True
    )
    schema: Mapped["SchemaDbo"] = relationship(back_populates="attributes")
