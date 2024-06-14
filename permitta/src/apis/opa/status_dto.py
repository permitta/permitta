from datetime import datetime

from pydantic import BaseModel, Field


class StatusLabelsDto(BaseModel):
    id: str = Field()
    version: str = Field()


class StatusTrinoBundleDto(BaseModel):
    name: str = Field()
    last_successful_activation: datetime = Field()
    type: str = Field()
    size: int = Field()
    last_successful_download: datetime = Field()
    last_successful_request: datetime = Field()


class StatusBundlesDto(BaseModel):
    trino: StatusTrinoBundleDto = Field()


class StatusDto(BaseModel):
    labels: StatusLabelsDto = Field()
    bundles: StatusBundlesDto = Field()
