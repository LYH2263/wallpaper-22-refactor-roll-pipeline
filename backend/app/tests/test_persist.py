"""Mapping-layer tests for app.repositories.persist.

Runs against a temporary sqlite database: write a breakdown, read it back
by id, and check the numbers survive the round trip unchanged — the mapping
must store/load, never recompute.
"""

import json

import pytest

from app import seed
from app.engines.breakdown import compute_breakdown
from app.repositories import history, persist


@pytest.fixture()
def tmp_db(tmp_path, monkeypatch):
    db_file = tmp_path / "persist_test.db"
    monkeypatch.setattr("app.db.DB_PATH", str(db_file))
    seed.init_db()
    return db_file


def test_write_then_read_back_rolls_consistent(tmp_db):
    # seeded ids: wall 1 = 主卧一圈, roll 1 = 素色53
    bd = compute_breakdown(16.0, 2.7, 0.53, 10.0, 0)
    run_id = persist.insert_breakdown(1, 1, bd, "主卧试算")

    detail = persist.get_run_detail(run_id)
    assert detail["id"] == run_id
    assert detail["result"]["rolls"] == bd.rolls == 11
    assert detail["result"] == bd.to_dict()
    assert detail["wall_name"] == "主卧一圈"
    assert detail["roll_name"] == "素色53"
    assert detail["note"] == "主卧试算"


def test_readback_is_verbatim_not_recomputed(tmp_db):
    # A stored row whose numbers contradict the engine must come back as
    # stored — proving the mapping never calls the roll engine.
    from app.db import connect

    conn = connect()
    try:
        cur = conn.execute(
            "INSERT INTO calc_runs(wall_id,roll_id,result_json,note,created_at) VALUES (?,?,?,?,?)",
            (1, 1, json.dumps({"drops": 1, "drop_len_m": 9.9, "pattern_m": 0.0,
                               "strips_per_roll": 1, "rolls": 999}), "doctored", "2026-01-01"),
        )
        conn.commit()
        run_id = int(cur.lastrowid)
    finally:
        conn.close()

    detail = persist.get_run_detail(run_id)
    assert detail["result"]["rolls"] == 999
    assert detail["result"]["drop_len_m"] == 9.9


def test_readback_tolerates_legacy_extra_keys(tmp_db):
    from app.db import connect

    legacy = {"drops": 31, "drop_len_m": 2.7, "pattern_m": 0.0, "strips_per_roll": 3,
              "rolls": 11, "wall_id": 1, "roll_id": 1}
    conn = connect()
    try:
        cur = conn.execute(
            "INSERT INTO calc_runs(wall_id,roll_id,result_json,note,created_at) VALUES (?,?,?,?,?)",
            (1, 1, json.dumps(legacy), "legacy", "2026-01-01"),
        )
        conn.commit()
        run_id = int(cur.lastrowid)
    finally:
        conn.close()

    assert persist.get_run_detail(run_id)["result"]["rolls"] == 11


def test_missing_run_returns_none(tmp_db):
    assert persist.get_run_detail(424242) is None


def test_list_and_detail_share_fields(tmp_db):
    bd = compute_breakdown(20.0, 2.8, 0.53, 10.0, 64)
    run_id = persist.insert_breakdown(2, 2, bd, "大花")

    listed = [item for item in history.list_runs() if item["id"] == run_id]
    assert len(listed) == 1
    detail = persist.get_run_detail(run_id)
    assert listed[0] == detail
    assert listed[0]["result"]["rolls"] == 19
