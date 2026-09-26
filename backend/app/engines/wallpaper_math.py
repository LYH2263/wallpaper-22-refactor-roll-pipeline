"""Wallpaper rolls: perimeter strips, pattern repeat on drop length, strips per roll.

Backward-compatible dict view over the pure breakdown computation in
app.engines.estimate_breakdown — the math lives there, this only re-shapes it.
"""

from app.engines.estimate_breakdown import compute_breakdown


def roll_count(
    perimeter: float,
    height: float,
    roll_width: float,
    roll_length: float,
    pattern_cm: float,
) -> dict:
    return compute_breakdown(perimeter, height, roll_width, roll_length, pattern_cm).to_dict()
