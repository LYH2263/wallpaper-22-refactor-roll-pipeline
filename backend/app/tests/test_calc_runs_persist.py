"""Persist mapping tests: write a Breakdown to calc_runs, read it back by id.

Uses a temporary sqlite database so the real app.db is never touched.
"""

import pytest

import app.db as db
from app import seed
from app.engines.estimate_breakdown import EstimateBreakdown, compute_breakdown
from app.repositories import calc_runs, rolls, walls


@pytest.fixture()
def temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    seed.init_db()


def test_save_then_read_back_rolls_consistent(temp_db):
    breakdown = compute_breakdown(16.0, 2.7, 0.53, 10.0, 0)
    run_id = calc_runs.save_breakdown(1, 1, breakdown, "主卧一圈×素色53")

    detail = calc_runs.get_run(run_id)
    assert detail["id"] == run_id
    assert detail["wall_id"] == 1
    assert detail["roll_id"] == 1
    assert detail["wall_name"] == "主卧一圈"
    assert detail["roll_name"] == "素色53"
    assert detail["note"] == "主卧一圈×素色53"
    assert detail["result"] == breakdown.to_dict()
    assert detail["result"]["rolls"] == 11


def test_read_back_never_recomputes(temp_db):
    # A breakdown the engine would never produce for these ids must survive
    # the write/read round trip untouched — the mapper does not recalculate.
    foreign = EstimateBreakdown(drops=1, drop_len_m=9.9, pattern_m=0.0, strips_per_roll=1, rolls=999)
    run_id = calc_runs.save_breakdown(1, 1, foreign)

    detail = calc_runs.get_run(run_id)
    assert detail["result"]["rolls"] == 999
    assert detail["result"] == foreign.to_dict()


def test_list_runs_uses_same_shape_as_detail(temp_db):
    breakdown = compute_breakdown(20.0, 2.8, 0.53, 10.0, 64)
    run_id = calc_runs.save_breakdown(2, 2, breakdown)

    items = calc_runs.list_runs()
    item = next(i for i in items if i["id"] == run_id)
    assert item["result"] == calc_runs.get_run(run_id)["result"]
    assert item["result"]["rolls"] == 19


def test_get_run_missing_returns_none(temp_db):
    assert calc_runs.get_run(424242) is None


def test_seed_pairs_keep_pre_refactor_numbers(temp_db):
    # 改造前口径：主卧一圈×素色53 = 11 卷，大花匹配×大花64 = 19 卷。
    wall, roll = walls.get_wall(1), rolls.get_roll(1)
    b1 = compute_breakdown(wall["perimeter"], wall["height"], roll["width"], roll["length"], roll["pattern_cm"])
    assert b1.rolls == 11

    wall, roll = walls.get_wall(2), rolls.get_roll(2)
    b2 = compute_breakdown(wall["perimeter"], wall["height"], roll["width"], roll["length"], roll["pattern_cm"])
    assert b2.rolls == 19
