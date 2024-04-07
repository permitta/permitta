import json
import uuid
from datetime import datetime

from database import Database
from models import PrincipalDbo, PrincipalAttributeDbo

process_id: str = str(uuid.uuid4())


def get_principal_dbo(mock_data: dict) -> PrincipalDbo:
    principal_dbo: PrincipalDbo = PrincipalDbo()
    principal_dbo.process_id = process_id
    principal_dbo.activated_at = datetime.now()
    principal_dbo.deactivated_at = None
    principal_dbo.first_name = mock_data.get("first_name")
    principal_dbo.last_name = mock_data.get("last_name")
    principal_dbo.user_name = (mock_data.get("first_name") + mock_data.get("last_name")).lower()
    principal_dbo.job_title = "Rubbish Collector"

    principal_dbo.principal_attributes = get_principal_attribute_dbos(mock_data=mock_data)
    return principal_dbo


def get_principal_attribute_dbos(mock_data: dict) -> list[PrincipalAttributeDbo]:
    keys: list[str] = ["email", "gender", "phone_number", "birthdate", "title", "picture"]

    principal_attribute_dbos: list[PrincipalAttributeDbo] = []
    for key in keys:
        principal_attribute_dbo: PrincipalAttributeDbo = PrincipalAttributeDbo()
        principal_attribute_dbo.process_id = process_id
        principal_attribute_dbo.activated_at = datetime.now()
        principal_attribute_dbo.deactivated_at = None
        principal_attribute_dbo.attribute_key = key
        principal_attribute_dbo.attribute_value = mock_data.get(key, "")
        principal_attribute_dbos.append(principal_attribute_dbo)
    return principal_attribute_dbos


with open("permitta/mock_data/principals.json") as json_file:
    mock_users: list[dict] = json.load(json_file)

principals: list[PrincipalDbo] = [
    get_principal_dbo(mock_user)
    for mock_user in mock_users
]

db = Database()
db.connect()

with db.Session.begin() as session:
    session.add_all(principals)
    session.commit()
