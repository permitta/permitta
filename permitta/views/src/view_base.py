from flask.views import MethodView

class ViewBase(MethodView):
    ROUTE_PREFIX: str = ""

    def __init__(self, model):
        pass
