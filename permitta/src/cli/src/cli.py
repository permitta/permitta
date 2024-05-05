import click
from database import Database
from ingestor import IngestionController


@click.group()
def cli():
    pass


@cli.command()
@click.option("--source", default="ldap", help="Source to ingest from")
def ingest(source):
    ingestion_controller = IngestionController()


if __name__ == "__main__":
    cli()
