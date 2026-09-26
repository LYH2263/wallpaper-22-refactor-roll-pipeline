"""Pure estimate breakdown: immutable roll-calculation result.

This module is the computational core behind the estimate boundary. It must
stay pure: no database, no network, no clock — only wall geometry and roll
parameters in, an immutable EstimateBreakdown out.
"""

from dataclasses import asdict, dataclass

from app.engines.helpers import ceil_units, floor_units


@dataclass(frozen=True)
class EstimateBreakdown:
    """Immutable result of one roll estimation."""

    drops: int
    drop_len_m: float
    pattern_m: float
    strips_per_roll: int
    rolls: int

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "EstimateBreakdown":
        """Rebuild a breakdown from a stored mapping; extra keys are ignored."""
        return cls(
            drops=int(data["drops"]),
            drop_len_m=float(data["drop_len_m"]),
            pattern_m=float(data["pattern_m"]),
            strips_per_roll=int(data["strips_per_roll"]),
            rolls=int(data["rolls"]),
        )


def compute_breakdown(
    perimeter: float,
    height: float,
    roll_width: float,
    roll_length: float,
    pattern_cm: float,
) -> EstimateBreakdown:
    """Derive the breakdown from wall geometry and roll parameters. Pure."""
    if roll_width <= 0 or roll_length <= 0:
        raise ValueError("invalid roll size")
    drops = ceil_units(float(perimeter) / float(roll_width))
    pattern_m = max(0.0, float(pattern_cm) / 100.0)
    drop_len = float(height) + pattern_m
    if drop_len <= 0:
        raise ValueError("invalid drop length")
    strips_per_roll = max(1, floor_units(float(roll_length) / drop_len))
    rolls = ceil_units(drops / strips_per_roll)
    return EstimateBreakdown(
        drops=drops,
        drop_len_m=round(drop_len, 3),
        pattern_m=round(pattern_m, 3),
        strips_per_roll=strips_per_roll,
        rolls=rolls,
    )
