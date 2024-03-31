from dataclasses import dataclass
from typing import Optional

from auth import OidcAuthProvider
from flask import Flask

from .healthz_view import HealthzGroupApi
from .principals_group_api import PrincipalsGroupApi
from .root_view import RootGroupApi
from .view_base import ViewBase


@dataclass
class Api:
    model: None
    item_api_class: Optional[ViewBase]
    group_api_class: Optional[ViewBase]


class ApiRegistrar:

    # TODO build this into the API class and load register all that inherit from base class
    apis: list[Api] = [
        # Api(
        #     model=None,
        #     item_api_class=None,
        #     group_api_class=RootGroupApi,
        # ),
        Api(
            model=None,
            item_api_class=None,
            group_api_class=PrincipalsGroupApi,
        ),
        Api(
            model=None,
            item_api_class=None,
            group_api_class=HealthzGroupApi,
        ),
    ]

    @staticmethod
    def _register_api(
        flask_app: Flask,
        model,
        oidc_auth_provider: OidcAuthProvider,
        item_api_class: ViewBase,
        group_api_class: ViewBase,
    ):
        # TODO deduplicate this
        if item_api_class:
            view_func = item_api_class.as_view(
                f"{item_api_class.ROUTE_PREFIX}-item", model, oidc_auth_provider
            )
            view_func = oidc_auth_provider.auth.oidc_auth(
                OidcAuthProvider.PROVIDER_NAME
            )(
                view_func
            )  # this is mental!

            flask_app.add_url_rule(
                f"/{item_api_class.ROUTE_PREFIX}/<int:id>", view_func=view_func
            )

        if group_api_class:
            view_func = group_api_class.as_view(
                f"{group_api_class.ROUTE_PREFIX}-group", model, oidc_auth_provider
            )
            view_func = oidc_auth_provider.auth.oidc_auth(
                OidcAuthProvider.PROVIDER_NAME
            )(
                view_func
            )  # this is mental!

            flask_app.add_url_rule(
                f"/{group_api_class.ROUTE_PREFIX}/", view_func=view_func
            )

    def init_app(self, flask_app: Flask, oidc_auth_provider: OidcAuthProvider):
        for api in self.apis:
            self._register_api(
                flask_app=flask_app,
                model=api.model,
                oidc_auth_provider=oidc_auth_provider,
                item_api_class=api.item_api_class,
                group_api_class=api.group_api_class,
            )
