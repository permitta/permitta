import click
from database import Database
from ingestor import IngestionController
from models import ObjectTypeEnum

@click.group()
def cli():
    pass


@cli.command()
@click.option("--source", default="ldap", help="Source to ingest from")
def ingest(source):
    ingestion_controller = IngestionController()
    ingestion_controller.ingest(connector_name=source, object_types=[ObjectTypeEnum.PRINCIPAL, ObjectTypeEnum.PRINCIPAL_ATTRIBUTE])


if __name__ == "__main__":
    cli()
