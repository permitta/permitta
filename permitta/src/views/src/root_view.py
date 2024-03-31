from flask import jsonify, render_template
from .view_base import ViewBase


class RootGroupApi(ViewBase):
    ROUTE_PREFIX = ""

    def get(self):
        return render_template("index.html")
