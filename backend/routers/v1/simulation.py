from fastapi import APIRouter, Depends, HTTPException
from schemas.simulation import SimulationConfig, SimulationResult
from services.calculator import CalculatorService

router = APIRouter()

@router.post("/run", response_model=SimulationResult)
def run_simulation(config: SimulationConfig):
    """
    Run a full ROI simulation based on the provided configuration.
    """
    try:
        result = CalculatorService.run_full_simulation(config)
        return result
    except Exception as e:
        # In a real app we'd log this error
        raise HTTPException(status_code=500, detail=str(e))
