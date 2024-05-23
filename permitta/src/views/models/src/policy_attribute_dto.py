from pydantic import BaseModel, Field


class PolicyAttributeDto(BaseModel):
    attributes: list[str] = Field()
