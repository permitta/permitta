from pydantic import BaseModel, Field


class PolicyMetadataDto(BaseModel):
    policy_id: int | None = Field()
    name: str = Field()
    description: str = Field()
