from typing import Optional

from pydantic import BaseModel, Field


class OpaQueryResponseModel(BaseModel):
    result: list[dict]
