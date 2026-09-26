"""Persistence mapping between EstimateBreakdown and calc_runs rows.

This layer only serializes what it is given and reads back what was stored —
it never recomputes roll numbers (no engine imports here on purpose).
"""

import json
from datetime import datetime, timezone

from app.db import connect
from app.engines.breakdown import EstimateBreakdown

_FIELDS = ("drops", "drop_len_m", "pattern_m", "strips_per_roll", "rolls")


def breakdown_to_json(breakdown: EstimateBreakdown) -> str:
    return json.dumps(breakdown.to_dict(), ensure_ascii=False)


def breakdown_from_json(result_json: str) -> EstimateBreakdown:
    """Rebuild the stored breakdown verbatim. Legacy rows may carry extra
    keys (wall_id/roll_id used to be embedded); only breakdown fields map."""
    data = json.loads(result_json)
    return EstimateBreakdown(
        drops=int(data["drops"]),
        drop_len_m=float(data["drop_len_m"]),
        pattern_m=float(data["pattern_m"]),
        strips_per_roll=int(data["strips_per_roll"]),
        rolls=int(data["rolls"]),
    )


def assemble_run(row) -> dict:
    """Row (calc_runs JOIN walls/rolls) -> history item. Shared by list and
    detail so every entry point reads the same stored fields."""
    item = dict(row)
    item["result"] = breakdown_from_json(item.pop("result_json")).to_dict()
    return item


def insert_breakdown(wall_id: int, roll_id: int, breakdown: EstimateBreakdown, note: str = "") -> int:
    conn = connect()
    try:
        cur = conn.execute(
            "INSERT INTO calc_runs(wall_id,roll_id,result_json,note,created_at) VALUES (?,?,?,?,?)",
            (
                wall_id,
                roll_id,
                breakdown_to_json(breakdown),
                note,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def get_run_detail(run_id: int):
    """Read one run back by id and assemble its history detail. Returns None
    when the id does not exist. Numbers come from storage, not the engine."""
    conn = connect()
    try:
        row = conn.execute(
            """
            SELECT r.*, w.name wall_name, rl.name roll_name
            FROM calc_runs r
            LEFT JOIN walls w ON w.id=r.wall_id
            LEFT JOIN rolls rl ON rl.id=r.roll_id
            WHERE r.id=?
            """,
            (run_id,),
        ).fetchone()
        return assemble_run(row) if row else None
    finally:
        conn.close()
