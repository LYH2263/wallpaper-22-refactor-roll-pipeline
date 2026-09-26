"""Breakdown core tests: pure computation only, no database involved."""

import dataclasses
import inspect

import pytest

from app.engines import estimate_breakdown
from app.engines.estimate_breakdown import EstimateBreakdown, compute_breakdown


def test_seed_pair_plain_master_bed_unchanged():
    # 种子：主卧一圈 (16.0m, 2.7m) × 素色53 (0.53m × 10m, 无对花)
    b = compute_breakdown(16.0, 2.7, 0.53, 10.0, 0)
    assert b.drops == 31
    assert b.drop_len_m == 2.7
    assert b.strips_per_roll == 3
    assert b.rolls == 11


def test_seed_pair_pattern_wall_unchanged():
    # 种子：大花匹配 (20.0m, 2.8m) × 大花64 (0.53m × 10m, 对花64cm)
    b = compute_breakdown(20.0, 2.8, 0.53, 10.0, 64)
    assert b.drops == 38
    assert b.drop_len_m == 3.44
    assert b.strips_per_roll == 2
    assert b.rolls == 19


def test_breakdown_is_immutable():
    b = compute_breakdown(16.0, 2.7, 0.53, 10.0, 0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        b.rolls = 99


def test_dict_round_trip():
    b = compute_breakdown(20.0, 2.8, 0.53, 10.0, 64)
    assert EstimateBreakdown.from_dict(b.to_dict()) == b


def test_from_dict_ignores_extra_keys():
    b = compute_breakdown(16.0, 2.7, 0.53, 10.0, 0)
    stored = {**b.to_dict(), "wall_id": 1, "roll_id": 2}
    assert EstimateBreakdown.from_dict(stored) == b


def test_invalid_roll_size_rejected():
    with pytest.raises(ValueError):
        compute_breakdown(16.0, 2.7, 0.0, 10.0, 0)


def test_module_stays_pure():
    src = inspect.getsource(estimate_breakdown)
    for banned in ("app.db", "sqlite3", "connect(", "requests", "urllib", "httpx", "socket"):
        assert banned not in src
