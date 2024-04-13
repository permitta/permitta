from database import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common_mixin_dbo import IngestionDboMixin


class DataObjectTableAttributeDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "data_object_table_attributes"

    data_object_attribute_id: int = Column(
        Integer, primary_key=True, autoincrement=True
    )
    attribute_key: str = Column(String)
    attribute_value: str = Column(String)

    data_object_table_id: Mapped[int] = mapped_column(
        ForeignKey("data_object_tables.data_object_table_id")
    )
    data_object_table: Mapped["DataObjectTableDbo"] = relationship(
        back_populates="data_object_table_attributes"
    )
