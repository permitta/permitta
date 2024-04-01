from unittest import mock

from pytest import fixture

from ..src.trino_client import TrinoClient
from ..src.trino_client_config import TrinoClientConfig


@fixture(scope="session")
def config() -> TrinoClientConfig:
    return TrinoClientConfig.load()


def mock_fetchmany_func(cursor, batch_size):
    yield [[1, "a"], [2, "b"]]
    yield [[3, "a"], [4, "b"]]
    yield [[5, "c"]]


@mock.patch.object(TrinoClient, "_get_cursor")
@mock.patch.object(TrinoClient, "_execute")
@mock.patch.object(TrinoClient, "_fetchmany", side_effect=mock_fetchmany_func)
@mock.patch.object(TrinoClient, "_get_schema", return_value=["id", "name"])
def test_execute_query(
    mock_get_schema: mock.MagicMock,
    mock_fetchmany: mock.MagicMock,
    mock_get_cursor: mock.MagicMock,
    mock_execute: mock.MagicMock,
    config: TrinoClientConfig,
):
    trino_client: TrinoClient = TrinoClient()

    loop_counter: int = 0
    records: list[dict] = []

    for batch in trino_client.select_async(query="select * from table", batch_size=2):
        loop_counter += 1
        records.extend(batch)

    # expect 3 batches
    assert loop_counter == 3

    assert records == [
        {"id": 1, "name": "a"},
        {"id": 2, "name": "b"},
        {"id": 3, "name": "a"},
        {"id": 4, "name": "b"},
        {"id": 5, "name": "c"},
    ]

    mock_execute.assert_called_once()
    mock_get_cursor.assert_called_once()
    mock_get_schema.assert_called_once()
    mock_fetchmany.assert_called_once()
