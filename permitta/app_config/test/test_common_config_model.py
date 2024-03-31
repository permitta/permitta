from ..src.common_config_model import CommonConfigModel


def test_constructor():
    common_config_model: CommonConfigModel = CommonConfigModel.load()
    assert common_config_model.db_connection_string == "sqlite:///:memory:"
    assert common_config_model.super_secret == "https:/domain?username=dont-tell-anyone"