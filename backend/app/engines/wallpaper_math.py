"""Wallpaper rolls: perimeter strips, pattern repeat on drop length, strips per roll.

Backwards-compatible dict facade over app.engines.breakdown — the pure,
immutable computation lives there; this wrapper only reshapes it.
"""

from app.engines.breakdown import compute_breakdown


def roll_count(
    perimeter: float,
    height: float,
    roll_width: float,
    roll_length: float,
    pattern_cm: float,
) -> dict:
    return compute_breakdown(perimeter, height, roll_width, roll_length, pattern_cm).to_dict()
