from dataclasses import dataclass

from .attribute_dto import AttributeDto


@dataclass
class TableDto:

    @property
    def f_q_table_name(self) -> str:
        return f"{self.platform_name}.{self.database_name}.{self.schema_name}.{self.table_name}"

    platform_id: int
    platform_name: str
    platform_attributes: list[AttributeDto]

    database_id: int
    database_name: str
    database_attributes: list[AttributeDto]

    schema_id: int
    schema_name: str
    schema_attributes: list[AttributeDto]

    table_id: int
    table_name: str
    table_attributes: list[AttributeDto]

    column_count: int

    accessible: bool | None = None
