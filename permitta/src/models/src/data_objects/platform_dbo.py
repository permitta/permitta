from database import BaseModel
from models.src.common_mixin_dbo import IngestionDboMixin
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class PlatformDbo(IngestionDboMixin, BaseModel):
    __tablename__ = "platforms"

    platform_id: int = Column(Integer, primary_key=True, autoincrement=True)
    platform_name: str = Column(String)
    platform_type: str = Column(String)

    databases: Mapped[list["DatabaseDbo"]] = relationship(back_populates="platform")

    attributes: Mapped[list["PlatformAttributeDbo"]] = relationship(
        back_populates="platform", cascade="all, delete"
    )


class PlatformAttributeDbo(BaseModel):
    __tablename__ = "platform_attributes"

    attribute_id: int = Column(Integer, primary_key=True, autoincrement=True)
    attribute_key: str = Column(String)
    attribute_value: str = Column(String)

    # # platform FK
    platform_id: Mapped[int] = mapped_column(
        ForeignKey("platforms.platform_id"), nullable=True
    )
    platform: Mapped["PlatformDbo"] = relationship(back_populates="attributes")
