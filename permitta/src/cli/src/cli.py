import click
from database import Database
from ingestor import LdapConnector


@click.group()
def cli():
    pass


@cli.command()
@click.option("--source", default="ldap", help="Source to ingest from")
def ingest(source):
    # todo move to ingestion manager(new name?)
    database: Database = Database()
    database.connect()
    ldap_connector: LdapConnector = LdapConnector(database=database)
    ldap_connector.ingest()


if __name__ == "__main__":
    cli()
