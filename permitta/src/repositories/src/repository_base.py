import inspect
from typing import Tuple, Type

from database import BaseModel, Database
from sqlalchemy import Row, and_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import ColumnProperty, Query, class_mapper
from sqlalchemy.sql.elements import NamedColumn


class RepositoryBase:

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_column_by_name(
        model: Type[BaseModel], column_name: str
    ) -> NamedColumn | ColumnProperty:
        matching_columns: list[ColumnProperty] = [
            c
            for c in [
                prop
                for prop in class_mapper(model).iterate_properties
                if isinstance(prop, ColumnProperty)
            ]
            if c.key == column_name
        ]
        if len(matching_columns) > 0:
            return matching_columns[0].columns[0]

        matching_hybrid_properties: list[hybrid_property] = [
            prop
            for prop in sa_inspect(model).all_orm_descriptors
            if type(prop) == hybrid_property and prop.__name__ == column_name
        ]
        if len(matching_hybrid_properties) > 0:
            return matching_hybrid_properties[0]

        raise KeyError(
            f"Column with name '{column_name}' does not exist in model: '{model}'"
        )

    @staticmethod
    def get_all_with_search_and_pagination(
        session,
        model: Type[BaseModel],
        sort_col_name: str,
        page_number: int,
        page_size: int,
        sort_ascending: bool = True,
        search_term: str = "",
        search_column_name: str = "search_property",
    ) -> Tuple[int, list[BaseModel]]:
        sort_column: NamedColumn | ColumnProperty = RepositoryBase.get_column_by_name(
            model=model, column_name=sort_col_name
        )

        search_column: NamedColumn | ColumnProperty = RepositoryBase.get_column_by_name(
            model=model, column_name=search_column_name
        )

        query: Query = session.query(model).filter(
            search_column.ilike(f"%{search_term}%")
        )
        count: int = query.count()

        results: list[BaseModel] = (
            query.order_by(sort_column)
            .slice(page_number * page_size, (page_number + 1) * page_size)
            .all()
        )
        return count, results
