"""
WASTESENSE API routes.

Member 5 — FastAPI + ML Integration
Database-backed endpoints will be connected to the repository layer
when the database integration is available.
"""

from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api", tags=["WASTESENSE API"])


def _not_implemented(endpoint: str) -> None:
    """Return a clear response until the required service is integrated."""
    raise HTTPException(
        status_code=501,
        detail=(
            f"{endpoint} is defined in the API contract, "
            "but its data service is not integrated yet."
        ),
    )


@router.get("/overview")
async def get_overview() -> dict[str, Any]:
    """Retrieve the system overview."""
    _not_implemented("GET /api/overview")


@router.get("/machines")
async def get_machines() -> dict[str, Any]:
    """Retrieve monitored machines."""
    _not_implemented("GET /api/machines")


@router.get("/machines/{machine_id}")
async def get_machine(machine_id: str) -> dict[str, Any]:
    """Retrieve details for a particular machine."""
    _not_implemented("GET /api/machines/{machine_id}")


@router.get("/workloads")
async def get_workloads() -> dict[str, Any]:
    """Retrieve workload records."""
    _not_implemented("GET /api/workloads")


@router.get("/waste")
async def get_waste() -> dict[str, Any]:
    """Retrieve detected resource-waste records."""
    _not_implemented("GET /api/waste")


@router.get("/waste/{waste_id}")
async def get_waste_record(waste_id: str) -> dict[str, Any]:
    """Retrieve a particular waste record."""
    _not_implemented("GET /api/waste/{waste_id}")


@router.get("/alerts")
async def get_alerts() -> dict[str, Any]:
    """Retrieve system alerts."""
    _not_implemented("GET /api/alerts")


@router.get("/trends")
async def get_trends() -> dict[str, Any]:
    """Retrieve resource-usage trends."""
    _not_implemented("GET /api/trends")


@router.get("/savings")
async def get_savings() -> dict[str, Any]:
    """Retrieve estimated resource savings."""
    _not_implemented("GET /api/savings")


@router.get("/replay/{waste_id}")
async def replay_waste(waste_id: str) -> dict[str, Any]:
    """Retrieve or run a replay for a waste record."""
    _not_implemented("GET /api/replay/{waste_id}")


@router.post("/optimization")
async def optimize_workload() -> dict[str, Any]:
    """Request workload optimization."""
    _not_implemented("POST /api/optimization")