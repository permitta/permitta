from flask import jsonify

from .view_base import ViewBase

# these should be *ItemApi or *GroupApi
# GroupApi is for those which don't have an id (get all / post)


class HealthzGroupApi(ViewBase):
    ROUTE_PREFIX: str = "healthz"

    def get(self):
        return jsonify(self.session.as_dict())
