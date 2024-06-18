from pydantic import BaseModel, Field


class PolicyAttributeDto(BaseModel):
    @property
    def attribute_list(self) -> list[str]:
        return (
            self.attributes if isinstance(self.attributes, list) else [self.attributes]
        )

    attributes: list[str] | str = Field()
