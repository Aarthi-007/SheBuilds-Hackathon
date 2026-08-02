from fastapi import APIRouter, HTTPException

from backend.agents.impact_simulation_agent import ImpactSimulationAgent
from backend.schemas.impact_simulation import ImpactSimulationReport, ImpactSimulationRequest

router = APIRouter(prefix="/impact-simulation", tags=["impact-simulation"])
_agent = ImpactSimulationAgent()


@router.post("", response_model=ImpactSimulationReport)
async def run_impact_simulation(request: ImpactSimulationRequest) -> ImpactSimulationReport:
    try:
        return await _agent.run(request)
    except ValueError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Impact simulation failed: {exc}") from exc
