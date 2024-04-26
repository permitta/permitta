from database import Database
from models import *

db: Database = Database()
db.connect()
db.create_all_tables()
