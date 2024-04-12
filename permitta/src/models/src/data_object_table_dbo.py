from database import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .common_mixin_dbo import IngestionDboMixin


class DataObjectTableDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "data_object_tables"

    data_object_table_id = Column(Integer, primary_key=True, autoincrement=True)
    database_name: str = Column(String)
    schema_name: str = Column(String)
    object_name: str = Column(String)

    # HACK there must be a cleverer way than this
    search_value: str = Column(String)

    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.platform_id"))
    platform: Mapped["PlatformDbo"] = relationship(back_populates="data_object_tables")

    data_object_table_attributes: Mapped[list["DataObjectTableAttributeDbo"]] = (
        relationship(back_populates="data_object_table")
    )
