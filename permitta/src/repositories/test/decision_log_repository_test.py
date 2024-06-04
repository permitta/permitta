from database import Database
from datetime import datetime, timezone
from models import DecisionLogDbo
from ..src.decision_log_repository import DecisionLogRepository


def test_create_execute_query() -> None:
    decision_log_dbo: DecisionLogDbo = DecisionLogRepository.create(
        decision_log={
            "labels": {
                "id": "337e33a2-7ee8-4dee-92d9-6db3b4294aba",
                "version": "0.64.1",
            },
            "decision_id": "f5c6415d-c013-4fef-8d1b-ec3830a82d0e",
            "path": "permitta/trino/allow",
            "input": {
                "action": {"operation": "ExecuteQuery"},
                "context": {
                    "identity": {"groups": [], "user": "alice"},
                    "softwareStack": {"trinoVersion": "448"},
                },
            },
            "result": True,
            "requested_by": "172.23.0.4:46008",
            "timestamp": "2024-06-03T21:06:50.686549126Z",
            "metrics": {
                "counter_server_query_cache_hit": 1,
                "timer_rego_external_resolve_ns": 792,
                "timer_rego_input_parse_ns": 46458,
                "timer_rego_query_eval_ns": 264125,
                "timer_server_handler_ns": 368708,
            },
            "req_id": 2682,
        }
    )

    assert decision_log_dbo.decision_log_id == "f5c6415d-c013-4fef-8d1b-ec3830a82d0e"
    assert decision_log_dbo.path == "permitta/trino/allow"
    assert decision_log_dbo.operation == "ExecuteQuery"
    assert decision_log_dbo.username == "alice"
    assert decision_log_dbo.permitted == True
    assert decision_log_dbo.timestamp == datetime(
        2024, 6, 3, 21, 6, 50, 686549, tzinfo=timezone.utc
    )


def test_create_get_column_masks_null() -> None:
    decision_log_dbo: DecisionLogDbo = DecisionLogRepository.create(
        decision_log={
            "labels": {
                "id": "337e33a2-7ee8-4dee-92d9-6db3b4294aba",
                "version": "0.64.1",
            },
            "decision_id": "303abc8a-ab73-4865-83e0-bd4cf935a83a",
            "path": "permitta/trino/columnmask",
            "input": {
                "action": {
                    "operation": "GetColumnMask",
                    "resource": {
                        "column": {
                            "catalogName": "iceberg",
                            "columnName": "a",
                            "columnType": "integer",
                            "schemaName": "logistics",
                            "tableName": "shippers",
                        }
                    },
                },
                "context": {
                    "identity": {"groups": [], "user": "alice"},
                    "softwareStack": {"trinoVersion": "448"},
                },
            },
            "requested_by": "172.23.0.4:46008",
            "timestamp": "2024-06-03T21:06:50.717566084Z",
            "metrics": {
                "counter_server_query_cache_hit": 1,
                "timer_rego_external_resolve_ns": 375,
                "timer_rego_input_parse_ns": 37417,
                "timer_rego_query_eval_ns": 264584,
                "timer_server_handler_ns": 338000,
            },
            "req_id": 2683,
        }
    )

    assert decision_log_dbo.operation == "GetColumnMask"
    assert decision_log_dbo.username == "alice"
    assert decision_log_dbo.permitted is None
    assert decision_log_dbo.expression is None

    assert decision_log_dbo.database == "iceberg"
    assert decision_log_dbo.schema == "logistics"
    assert decision_log_dbo.table == "shippers"
    assert decision_log_dbo.column == "a"


def test_create_get_column_masks_not_null() -> None:
    decision_log_dbo: DecisionLogDbo = DecisionLogRepository.create(
        decision_log={
            "labels": {
                "id": "337e33a2-7ee8-4dee-92d9-6db3b4294aba",
                "version": "0.64.1",
            },
            "decision_id": "2e544296-4281-427d-8c75-3f8a89d074a0",
            "path": "permitta/trino/columnmask",
            "input": {
                "action": {
                    "operation": "GetColumnMask",
                    "resource": {
                        "column": {
                            "catalogName": "iceberg",
                            "columnName": "c",
                            "columnType": "integer",
                            "schemaName": "logistics",
                            "tableName": "shippers",
                        }
                    },
                },
                "context": {
                    "identity": {"groups": [], "user": "alice"},
                    "softwareStack": {"trinoVersion": "448"},
                },
            },
            "result": {"expression": "NULL"},
            "requested_by": "172.23.0.4:46008",
            "timestamp": "2024-06-03T21:06:50.720435417Z",
            "metrics": {
                "counter_server_query_cache_hit": 1,
                "timer_rego_external_resolve_ns": 542,
                "timer_rego_input_parse_ns": 43709,
                "timer_rego_query_eval_ns": 393917,
                "timer_server_handler_ns": 466042,
            },
            "req_id": 2685,
        }
    )

    assert decision_log_dbo.operation == "GetColumnMask"
    assert decision_log_dbo.username == "alice"
    assert decision_log_dbo.permitted is True
    assert decision_log_dbo.expression == "NULL"

    assert decision_log_dbo.database == "iceberg"
    assert decision_log_dbo.schema == "logistics"
    assert decision_log_dbo.table == "shippers"
    assert decision_log_dbo.column == "c"


def test_create_select_from_columns() -> None:
    decision_log_dbo: DecisionLogDbo = DecisionLogRepository.create(
        {
            "labels": {
                "id": "337e33a2-7ee8-4dee-92d9-6db3b4294aba",
                "version": "0.64.1",
            },
            "decision_id": "12007ca2-c0c2-4654-9e37-06acfc2f21e9",
            "path": "permitta/trino/allow",
            "input": {
                "action": {
                    "operation": "SelectFromColumns",
                    "resource": {
                        "table": {
                            "catalogName": "iceberg",
                            "columns": ["c"],
                            "schemaName": "logistics",
                            "tableName": "shippers",
                        }
                    },
                },
                "context": {
                    "identity": {"groups": [], "user": "alice"},
                    "softwareStack": {"trinoVersion": "448"},
                },
            },
            "result": True,
            "requested_by": "172.23.0.4:46008",
            "timestamp": "2024-06-03T21:06:50.723272167Z",
            "metrics": {
                "counter_server_query_cache_hit": 1,
                "timer_rego_external_resolve_ns": 374,
                "timer_rego_input_parse_ns": 21834,
                "timer_rego_query_eval_ns": 255583,
                "timer_server_handler_ns": 317042,
            },
            "req_id": 2687,
        }
    )

    assert decision_log_dbo.operation == "SelectFromColumns"
    assert decision_log_dbo.username == "alice"
    assert decision_log_dbo.permitted is True
    assert decision_log_dbo.expression is None

    assert decision_log_dbo.database == "iceberg"
    assert decision_log_dbo.schema == "logistics"
    assert decision_log_dbo.table == "shippers"
    assert decision_log_dbo.column == "c"


def test_create_access_catalog() -> None:
    decision_log_dbo: DecisionLogDbo = DecisionLogRepository.create(
        {
            "labels": {
                "id": "337e33a2-7ee8-4dee-92d9-6db3b4294aba",
                "version": "0.64.1",
            },
            "decision_id": "9e72d7e1-2979-449a-a57c-4f0a94ea3cd3",
            "path": "permitta/trino/allow",
            "input": {
                "action": {
                    "operation": "AccessCatalog",
                    "resource": {"catalog": {"name": "iceberg"}},
                },
                "context": {
                    "identity": {"groups": [], "user": "alice"},
                    "softwareStack": {"trinoVersion": "448"},
                },
            },
            "result": True,
            "requested_by": "172.23.0.4:46008",
            "timestamp": "2024-06-03T21:06:50.721700417Z",
            "metrics": {
                "counter_server_query_cache_hit": 1,
                "timer_rego_external_resolve_ns": 291,
                "timer_rego_input_parse_ns": 25208,
                "timer_rego_query_eval_ns": 146375,
                "timer_server_handler_ns": 202000,
            },
            "req_id": 2686,
        }
    )

    assert decision_log_dbo.operation == "AccessCatalog"
    assert decision_log_dbo.username == "alice"
    assert decision_log_dbo.permitted is True
    assert decision_log_dbo.expression is None

    assert decision_log_dbo.database == "iceberg"
    assert decision_log_dbo.schema is None
    assert decision_log_dbo.table is None
    assert decision_log_dbo.column is None


def test_create_filter_catalog() -> None:
    decision_log_dbo: DecisionLogDbo = DecisionLogRepository.create(
        {
            "labels": {
                "id": "337e33a2-7ee8-4dee-92d9-6db3b4294aba",
                "version": "0.64.1",
            },
            "decision_id": "9e72d7e1-2979-449a-a57c-4f0a94ea3cd3",
            "path": "permitta/trino/allow",
            "input": {
                "action": {
                    "operation": "FilterCatalogs",
                    "resource": {"catalog": {"name": "system"}},
                },
                "context": {"identity": {"user": "alice"}},
            },
            "result": True,
            "requested_by": "172.23.0.4:46008",
            "timestamp": "2024-06-03T21:06:50.721700417Z",
            "metrics": {
                "counter_server_query_cache_hit": 1,
                "timer_rego_external_resolve_ns": 291,
                "timer_rego_input_parse_ns": 25208,
                "timer_rego_query_eval_ns": 146375,
                "timer_server_handler_ns": 202000,
            },
            "req_id": 2686,
        }
    )

    assert decision_log_dbo.operation == "FilterCatalogs"
    assert decision_log_dbo.username == "alice"
    assert decision_log_dbo.permitted is True
    assert decision_log_dbo.expression is None

    assert decision_log_dbo.database == "system"
    assert decision_log_dbo.schema is None
    assert decision_log_dbo.table is None
    assert decision_log_dbo.column is None


def test_create_filter_tables() -> None:
    decision_log_dbo: DecisionLogDbo = DecisionLogRepository.create(
        {
            "labels": {
                "id": "337e33a2-7ee8-4dee-92d9-6db3b4294aba",
                "version": "0.64.1",
            },
            "decision_id": "9e72d7e1-2979-449a-a57c-4f0a94ea3cd3",
            "path": "permitta/trino/allow",
            "input": {
                "action": {
                    "operation": "FilterTables",
                    "resource": {
                        "table": {
                            "catalogName": "iceberg",
                            "schemaName": "hr",
                            "tableName": "employees",
                        }
                    },
                },
                "context": {"identity": {"user": "alice"}},
            },
            "result": True,
            "requested_by": "172.23.0.4:46008",
            "timestamp": "2024-06-03T21:06:50.721700417Z",
            "metrics": {
                "counter_server_query_cache_hit": 1,
                "timer_rego_external_resolve_ns": 291,
                "timer_rego_input_parse_ns": 25208,
                "timer_rego_query_eval_ns": 146375,
                "timer_server_handler_ns": 202000,
            },
            "req_id": 2686,
        }
    )

    assert decision_log_dbo.operation == "FilterTables"
    assert decision_log_dbo.username == "alice"
    assert decision_log_dbo.permitted is True
    assert decision_log_dbo.expression is None

    assert decision_log_dbo.database == "iceberg"
    assert decision_log_dbo.schema == "hr"
    assert decision_log_dbo.table == "employees"
    assert decision_log_dbo.column == ""


def test_create_filter_columns() -> None:
    decision_log_dbo: DecisionLogDbo = DecisionLogRepository.create(
        {
            "labels": {
                "id": "337e33a2-7ee8-4dee-92d9-6db3b4294aba",
                "version": "0.64.1",
            },
            "decision_id": "9e72d7e1-2979-449a-a57c-4f0a94ea3cd3",
            "path": "permitta/trino/allow",
            "input": {
                "action": {
                    "operation": "FilterColumns",
                    "resource": {
                        "table": {
                            "catalogName": "iceberg",
                            "columns": ["column1"],
                            "schemaName": "logistics",
                            "tableName": "regions",
                        }
                    },
                },
                "context": {"identity": {"user": "alice"}},
            },
            "result": True,
            "requested_by": "172.23.0.4:46008",
            "timestamp": "2024-06-03T21:06:50.721700417Z",
            "metrics": {
                "counter_server_query_cache_hit": 1,
                "timer_rego_external_resolve_ns": 291,
                "timer_rego_input_parse_ns": 25208,
                "timer_rego_query_eval_ns": 146375,
                "timer_server_handler_ns": 202000,
            },
            "req_id": 2686,
        }
    )

    assert decision_log_dbo.operation == "FilterColumns"
    assert decision_log_dbo.username == "alice"
    assert decision_log_dbo.permitted is True
    assert decision_log_dbo.expression is None

    assert decision_log_dbo.database == "iceberg"
    assert decision_log_dbo.schema == "logistics"
    assert decision_log_dbo.table == "regions"
    assert decision_log_dbo.column == "column1"
