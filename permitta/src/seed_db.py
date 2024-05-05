from database import Database, DatabaseSeeder

db: Database = Database()
db.connect()
db.drop_all_tables()
db.create_all_tables()
database_seeder: DatabaseSeeder = DatabaseSeeder(db=db)
database_seeder.seed()
