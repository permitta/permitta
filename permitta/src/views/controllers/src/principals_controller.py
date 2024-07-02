from typing import Tuple

from app_logger import Logger, get_logger
from models import AttributeDto, PrincipalDbo
from repositories import PrincipalRepository

logger: Logger = get_logger("controller.principals")


class PrincipalsController:

    @staticmethod
    def get_all_principals_with_search_pagination_and_attr_filter(
        session,
        sort_col_name: str,
        page_number: int,
        page_size: int,
        sort_ascending: bool = True,
        search_term: str = "",
        attributes: list[AttributeDto] = None,
    ) -> Tuple[int, list[PrincipalDbo]]:
        repo: PrincipalRepository = PrincipalRepository()

        # if we dont have attributes we can use the fast one
        if attributes is None:
            return repo.get_all_with_search_and_pagination(
                session=session,
                sort_col_name=sort_col_name,
                page_number=page_number,
                page_size=page_size,
                sort_ascending=sort_ascending,
                search_term=search_term,
            )
        sort_col_name = f"principals.{sort_col_name}"
        return repo.get_all_with_search_and_pagination_and_attr_filter(
            session=session,
            sort_col_name=sort_col_name,
            page_number=page_number,
            page_size=page_size,
            sort_ascending=sort_ascending,
            search_term=search_term,
            attributes=attributes,
        )
