from dataclasses import dataclass

from .attribute_dto import AttributeDto


@dataclass
class SchemaDto:
    @property
    def f_q_schema_name(self) -> str:
        return f"{self.platform_name}.{self.database_name}.{self.schema_name}"

    platform_id: int
    platform_name: str
    platform_attributes: list[AttributeDto]

    database_id: int
    database_name: str
    database_attributes: list[AttributeDto]

    schema_id: int
    schema_name: str
    schema_attributes: list[AttributeDto]

    accessible: bool | None
    child_count: int
