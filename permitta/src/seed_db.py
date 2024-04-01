import json
import uuid
from datetime import datetime

from database import Database
from models import PrincipalDbo

process_id: str = str(uuid.uuid4())


def get_principal_dbo(first_name: str, last_name: str) -> PrincipalDbo:
    principal_dbo: PrincipalDbo = PrincipalDbo()
    principal_dbo.process_id = process_id
    principal_dbo.activated_at = datetime.now()
    principal_dbo.deactivated_at = None
    principal_dbo.first_name = first_name
    principal_dbo.last_name = last_name
    principal_dbo.user_name = (first_name + last_name).lower()
    principal_dbo.job_title = "Rubbish Collector"
    return principal_dbo


with open("permitta/mock_data/principals.json") as json_file:
    mock_users: list[dict] = json.load(json_file)

principals: list[PrincipalDbo] = [
    get_principal_dbo(mock_user.get("first_name"), mock_user.get("last_name"))
    for mock_user in mock_users
]

db = Database()
db.connect()

with db.Session.begin() as session:
    session.add_all(principals)
    session.commit()
