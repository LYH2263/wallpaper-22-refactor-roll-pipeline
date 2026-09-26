from app.db import connect
from app.repositories.persist import assemble_run


def list_runs(limit: int = 50):
    conn = connect()
    try:
        rows = conn.execute(
            """
            SELECT r.*, w.name wall_name, rl.name roll_name
            FROM calc_runs r
            LEFT JOIN walls w ON w.id=r.wall_id
            LEFT JOIN rolls rl ON rl.id=r.roll_id
            ORDER BY r.id DESC LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [assemble_run(row) for row in rows]
    finally:
        conn.close()
