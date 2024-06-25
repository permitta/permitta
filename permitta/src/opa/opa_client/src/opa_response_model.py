from pydantic import BaseModel, Field
from typing import Optional


class OpaResponseModel(BaseModel):
    result: Optional[bool] = False
