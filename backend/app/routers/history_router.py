from fastapi import APIRouter, HTTPException
from app.repositories import history as repo
from app.repositories import persist

router = APIRouter()


@router.get("/runs")
def list_runs(limit: int = 50):
    return {"items": repo.list_runs(limit)}


@router.get("/runs/{run_id}")
def run_detail(run_id: int):
    detail = persist.get_run_detail(run_id)
    if not detail:
        raise HTTPException(404, "run not found")
    return detail
