from enum import Enum

from models import PolicyDbo
from pydantic import BaseModel, Field


class PolicyTypeEnum(Enum):
    BUILDER = PolicyDbo.POLICY_TYPE_BUILDER
    DSL = PolicyDbo.POLICY_TYPE_DSL


class PolicyCreateVm(BaseModel):
    policy_type: PolicyTypeEnum = Field()
