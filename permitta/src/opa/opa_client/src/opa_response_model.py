from pydantic import BaseModel, Field


class OpaResponseAllowModel(BaseModel):
    allow: bool = Field()


class OpaResponseModel(BaseModel):
    result: OpaResponseAllowModel = Field()
