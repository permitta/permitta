from database import BaseModel
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .common_mixin_dbo import CommonMixinDbo


class DataObjectTableDbo(CommonMixinDbo, BaseModel):
    __tablename__ = 'data_object_tables'

    data_object_table_id = Column(Integer, primary_key=True)
    database_name: str = Column(String)
    schema_name: str = Column(String)
    object_name: str = Column(String)

    # HACK there must be a cleverer way than this
    search_value: str = Column(String)

    platform_id: Mapped[int] = mapped_column(ForeignKey("platforms.platform_id"))
    platform: Mapped["PlatformDbo"] = relationship(back_populates="data_object_tables")