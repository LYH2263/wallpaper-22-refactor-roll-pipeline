"""Pure-function tests for EstimateBreakdown / compute_breakdown.

No database, no network — this file must stay importable and runnable
without any fixture beyond plain values.
"""

import dataclasses

import pytest

from app.engines.breakdown import EstimateBreakdown, compute_breakdown


def test_seed_plain_master_bed_unchanged():
    # 主卧一圈 16.0m x 2.7m + 素色53 (0.53m x 10.0m, no pattern)
    bd = compute_breakdown(16.0, 2.7, 0.53, 10.0, 0)
    assert bd.drops == 31
    assert bd.drop_len_m == 2.7
    assert bd.pattern_m == 0.0
    assert bd.strips_per_roll == 3
    assert bd.rolls == 11


def test_seed_pattern_wall_unchanged():
    # 大花匹配 20.0m x 2.8m + 大花64 (0.53m x 10.0m, 64cm repeat)
    bd = compute_breakdown(20.0, 2.8, 0.53, 10.0, 64)
    assert bd.drops == 38
    assert bd.drop_len_m == 3.44
    assert bd.pattern_m == 0.64
    assert bd.strips_per_roll == 2
    assert bd.rolls == 19


def test_breakdown_is_immutable():
    bd = compute_breakdown(16.0, 2.7, 0.53, 10.0, 0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        bd.rolls = 99


def test_to_dict_roundtrip_keys():
    bd = compute_breakdown(4.0, 2.5, 0.53, 10.0, 0)
    d = bd.to_dict()
    assert d == {
        "drops": bd.drops,
        "drop_len_m": bd.drop_len_m,
        "pattern_m": bd.pattern_m,
        "strips_per_roll": bd.strips_per_roll,
        "rolls": bd.rolls,
    }
    assert EstimateBreakdown(**d) == bd


def test_invalid_roll_size_rejected():
    with pytest.raises(ValueError):
        compute_breakdown(16.0, 2.7, 0.0, 10.0, 0)
    with pytest.raises(ValueError):
        compute_breakdown(16.0, 2.7, 0.53, 0.0, 0)


def test_negative_pattern_counts_as_plain():
    assert compute_breakdown(16.0, 2.7, 0.53, 10.0, -5) == compute_breakdown(16.0, 2.7, 0.53, 10.0, 0)
