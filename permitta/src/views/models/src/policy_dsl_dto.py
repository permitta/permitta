from pydantic import BaseModel, Field


class PolicyDslDto(BaseModel):
    policy_dsl: str = Field()
