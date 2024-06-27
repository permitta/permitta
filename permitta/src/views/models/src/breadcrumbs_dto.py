from pydantic import BaseModel


class BreadcrumbsDto(BaseModel):
    items: list[str]
