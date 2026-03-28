import pytest

from hive_copilot.backend.app.services.hive_execution_service import sanitize_sql


def test_allows_select_single_statement():
    sql = "SELECT * FROM business"
    assert sanitize_sql(sql) == "SELECT * FROM business"


def test_rejects_multiple_statements():
    with pytest.raises(ValueError):
        sanitize_sql("SELECT * FROM business; DROP TABLE x")


def test_rejects_non_select():
    with pytest.raises(ValueError):
        sanitize_sql("DELETE FROM business")


def test_rejects_dangerous_keyword_embedded():
    with pytest.raises(ValueError):
        sanitize_sql("WITH t AS (SELECT 1) UPDATE foo SET bar=1")
