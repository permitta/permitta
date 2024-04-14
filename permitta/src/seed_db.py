import os
from database import DatabaseSeeder

try:
    os.remove("permitta/instance/permitta.db")
except FileNotFoundError:
    pass

database_seeder: DatabaseSeeder = DatabaseSeeder()
database_seeder.seed()
