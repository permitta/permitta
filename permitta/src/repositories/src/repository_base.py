import inspect
from typing import Tuple, Type

from database import BaseModel, Database
from models import AttributeDto
from sqlalchemy import and_, desc, func, or_
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.inspection import inspect as sa_inspect
from sqlalchemy.orm import ColumnProperty, Query, class_mapper
from sqlalchemy.sql.elements import NamedColumn


class RepositoryBase:

    def __init__(self) -> None:
        pass

    @staticmethod
    def get_attribute_dtos(
        model, attribute_list_property_name: str = "attributes"
    ) -> list[AttributeDto]:
        return [
            AttributeDto(
                attribute_key=a.attribute_key, attribute_value=a.attribute_value
            )
            for a in getattr(model, attribute_list_property_name)
        ]

    @staticmethod
    def get_model_by_name(table_name: str) -> Type[BaseModel]:
        matching_models: list[BaseModel] = [
            cls for cls in BaseModel.__subclasses__() if cls.__tablename__ == table_name
        ]
        if not matching_models:
            raise ValueError(f"No model found for table {table_name}")
        return matching_models[0]

    @staticmethod
    def get_column_by_name(
        table_name: str, column_name: str
    ) -> NamedColumn | ColumnProperty:
        model: BaseModel = RepositoryBase.get_model_by_name(table_name=table_name)

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
    def _get_all_with_search_and_pagination(
        session,
        model: Type[BaseModel],
        page_number: int,
        page_size: int,
        search_column_names: list[str],
        sort_ascending: bool = True,
        sort_col_name: str | None = None,
        search_term: str = "",
    ) -> Tuple[int, list[BaseModel]]:
        query: Query = session.query(model)
        query = RepositoryBase._get_search_query(
            query=query,
            search_column_names=[
                f"{model.__tablename__}.{s}" for s in search_column_names
            ],
            search_term=search_term,
        )

        count: int = query.count()

        if sort_col_name:
            query = RepositoryBase._get_sort_query(
                query=query,
                sort_col_name=f"{model.__tablename__}.{sort_col_name}",
                sort_ascending=sort_ascending,
            )

        query: Query = RepositoryBase._get_pagination_query(
            query=query, page_number=page_number, page_size=page_size
        )

        results: list[BaseModel] = query.all()
        return count, results

    @staticmethod
    def _get_search_query(
        query: Query,
        search_column_names: list[str],
        search_term: str = "",
    ) -> Query:
        search_columns: list[NamedColumn] | list[ColumnProperty] = [
            RepositoryBase.get_column_by_name(
                table_name=search_column_name.split(".")[0],
                column_name=search_column_name.split(".")[1],
            )
            for search_column_name in search_column_names
        ]

        query = query.filter(
            or_(
                *[
                    search_column.ilike(f"%{search_term}%")
                    for search_column in search_columns
                ]
            )
        )
        return query

    @staticmethod
    def _get_sort_query(
        query: Query, sort_col_name: str, sort_ascending: bool = True
    ) -> Query:
        sort_column: NamedColumn | ColumnProperty = RepositoryBase.get_column_by_name(
            table_name=sort_col_name.split(".")[0],
            column_name=sort_col_name.split(".")[1],
        )
        if sort_ascending:
            query = query.order_by(sort_column)
        else:
            query = query.order_by(desc(sort_column))
        return query

    @staticmethod
    def _get_pagination_query(query: Query, page_number: int, page_size: int):
        return query.slice(page_number * page_size, (page_number + 1) * page_size)
