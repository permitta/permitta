from flask import Flask
from flask.views import MethodView
from .view_base import ViewBase
from .healthz_view import HealthzGroupApi
from dataclasses import dataclass
from typing import Optional


@dataclass
class Api:
    model: None
    item_api_class: Optional[ViewBase]
    group_api_class: Optional[ViewBase]


class ApiRegistrar:
    apis: list[Api] = [
        Api(
            model=None,
            item_api_class=None,
            group_api_class=HealthzGroupApi,
        )
    ]

    @staticmethod
    def _register_api(
        flask_app: Flask,
        model,
        item_api_class: ViewBase,
        group_api_class: ViewBase,
    ):
        if item_api_class:
            flask_app.add_url_rule(
                f"/{item_api_class.ROUTE_PREFIX}/<int:id>",
                view_func=item_api_class.as_view(f"{item_api_class.ROUTE_PREFIX}-item", model),
            )

        if group_api_class:
            flask_app.add_url_rule(
                f"/{group_api_class.ROUTE_PREFIX}/", view_func=group_api_class.as_view(f"{group_api_class.ROUTE_PREFIX}-group", model)
            )

    def init_app(self, flask_app: Flask):
        for api in self.apis:
            self._register_api(
                flask_app=flask_app,
                model=api.model,
                item_api_class=api.item_api_class,
                group_api_class=api.group_api_class,
            )