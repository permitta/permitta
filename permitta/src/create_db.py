from database import Database
from models import *

db: Database = Database()
db.connect()
db.drop_all_tables()
db.create_all_tables()
