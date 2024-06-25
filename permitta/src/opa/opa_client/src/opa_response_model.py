from pydantic import BaseModel, Field
from typing import Optional


class OpaResponseAllowModel(BaseModel):
    allow: bool = Field()


class OpaResponseModel(BaseModel):
    result: Optional[OpaResponseAllowModel] = OpaResponseAllowModel(allow=False)
