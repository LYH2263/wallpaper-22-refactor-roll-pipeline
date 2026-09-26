"""Persist mapping between EstimateBreakdown and the calc_runs table.

This module is a mapper, not a calculator: it serializes an already-computed
EstimateBreakdown into calc_runs and assembles history entries back from the
stored JSON. It never calls the roll engine — numbers are never recomputed
on the read path, so a saved run always reads back exactly what was written.
"""

import json
from datetime import datetime, timezone

from app.db import connect
from app.engines.estimate_breakdown import EstimateBreakdown

_SELECT_WITH_NAMES = """
    SELECT r.*, w.name wall_name, rl.name roll_name
    FROM calc_runs r
    LEFT JOIN walls w ON w.id=r.wall_id
    LEFT JOIN rolls rl ON rl.id=r.roll_id
"""


def save_breakdown(wall_id: int, roll_id: int, breakdown: EstimateBreakdown, note: str = "") -> int:
    """Write one computed breakdown as a calc_runs row; return the run id."""
    payload = {"wall_id": wall_id, "roll_id": roll_id, **breakdown.to_dict()}
    conn = connect()
    try:
        cur = conn.execute(
            "INSERT INTO calc_runs(wall_id,roll_id,result_json,note,created_at) VALUES (?,?,?,?,?)",
            (wall_id, roll_id, json.dumps(payload, ensure_ascii=False), note, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def get_run(run_id: int):
    """Read one run back by id and assemble its history detail, or None."""
    conn = connect()
    try:
        row = conn.execute(_SELECT_WITH_NAMES + " WHERE r.id=?", (run_id,)).fetchone()
        return _assemble(row) if row else None
    finally:
        conn.close()


def list_runs(limit: int = 50):
    """List recent runs, newest first, each assembled like a detail entry."""
    conn = connect()
    try:
        rows = conn.execute(_SELECT_WITH_NAMES + " ORDER BY r.id DESC LIMIT ?", (limit,)).fetchall()
        return [_assemble(row) for row in rows]
    finally:
        conn.close()


def _assemble(row) -> dict:
    """Map a calc_runs row to a history entry whose result is the stored breakdown."""
    d = dict(row)
    stored = json.loads(d.pop("result_json"))
    d["result"] = EstimateBreakdown.from_dict(stored).to_dict()
    return d
