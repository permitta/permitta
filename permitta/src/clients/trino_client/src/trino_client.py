from trino.auth import BasicAuthentication
from trino.dbapi import Cursor, connect

from .trino_client_config import TrinoClientConfig


class TrinoClient:
    trino_connection = None

    def __init__(self):
        config: TrinoClientConfig = TrinoClientConfig.load()
        self.trino_connection = connect(
            host=config.host,
            port=config.port,
            user=config.username,
            auth=BasicAuthentication(config.username, config.password),
        )

    def select_async(self, query: str, batch_size: int = 1000) -> list[dict]:
        cursor: Cursor = self._get_cursor()
        self._execute(cursor=cursor, query=query)

        schema: list[str] = self._get_schema(cursor=cursor)

        for batch in self._fetchmany(cursor=cursor, batch_size=batch_size):
            yield [{schema[i]: row[i] for i, _ in enumerate(schema)} for row in batch]

    def _get_cursor(self) -> Cursor:
        return self.trino_connection.cursor()

    def _execute(self, cursor: Cursor, query: str) -> None:
        cursor.execute(query)

    def _fetchmany(self, cursor: Cursor, batch_size: int) -> list[list]:
        return cursor.fetchmany(size=batch_size)

    def _get_schema(self, cursor: Cursor) -> list[str]:
        return [c.name for c in cursor.description]
