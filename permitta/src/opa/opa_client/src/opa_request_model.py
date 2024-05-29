from pydantic import BaseModel, Field


class OpaRequestInputModel(BaseModel):
    request_method: str = Field()


class OpaRequestModel(BaseModel):
    input: OpaRequestInputModel = Field()
