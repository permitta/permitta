import json
from unittest import mock

from clients import LdapClient
from repositories import PrincipalGroupRepository, PrincipalRepository

from ..src.ldap_connector import LdapConnector

with open("permitta/src/ingestor/connectors/ldap_connector/test/ldap_users.json") as f:
    ldap_users: list[dict] = json.load(f)


@mock.patch.object(LdapClient, "connect")
@mock.patch.object(LdapClient, "list_users", return_value=ldap_users)
def test_acquire_data(mock_list_users: mock.MagicMock, mock_connect: mock.MagicMock):
    ldap_connector: LdapConnector = LdapConnector()
    ldap_connector.acquire_data()

    mock_list_users.assert_called_with(
        user_search_base="ou=people,dc=example,dc=com",
        user_search_filter="(&(uid=*)(memberof=cn=permitta_users_gl,ou=groups,dc=example,dc=com))",
        attributes=["cn", "uid", "givenname", "sn", "mail", "memberOf"],
    )
    mock_connect.assert_called_once()


def test_get_principals():
    assert False


def test_get_principal_attributes():
    assert False
