from dataclasses import dataclass

from .attribute_dto import AttributeDto
from .schema_dto import SchemaDto


@dataclass
class TableDto(SchemaDto):
    @property
    def f_q_table_name(self) -> str:
        return f"{self.platform_name}.{self.database_name}.{self.schema_name}.{self.table_name}"

    table_id: int
    table_name: str
    table_attributes: list[AttributeDto]
