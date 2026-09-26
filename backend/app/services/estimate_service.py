from fastapi import HTTPException

from app.engines.estimate_breakdown import compute_breakdown
from app.repositories import calc_runs, rolls, walls


def run_estimate(wall_id: int, roll_id: int, save: bool, note: str):
    wall = walls.get_wall(wall_id)
    if not wall:
        raise HTTPException(404, "wall not found")
    roll = rolls.get_roll(roll_id)
    if not roll:
        raise HTTPException(404, "roll not found")
    if wall.get("data_quality") == "dirty" or roll.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty seed entity")

    breakdown = compute_breakdown(
        wall["perimeter"], wall["height"], roll["width"], roll["length"], roll["pattern_cm"]
    )
    run_id = None
    if save:
        run_id = calc_runs.save_breakdown(wall_id, roll_id, breakdown, note)
    return {"wall": wall, "roll": roll, "run_id": run_id, **breakdown.to_dict()}
