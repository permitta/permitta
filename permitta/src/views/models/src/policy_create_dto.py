from pydantic import BaseModel, Field
from models import PolicyDbo
from enum import Enum


class PolicyTypeEnum(Enum):
    BUILDER = PolicyDbo.POLICY_TYPE_BUILDER
    DSL = PolicyDbo.POLICY_TYPE_DSL


class PolicyCreateDto(BaseModel):
    policy_type: PolicyTypeEnum = Field()
