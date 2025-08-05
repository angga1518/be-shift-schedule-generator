from fastapi import APIRouter, HTTPException
from ..models.schemas import ScheduleRequest, ScheduleResponse, Shift
from ..solver.schedule_solver import ScheduleSolver

router = APIRouter()

@router.post("/generate-schedule", response_model=ScheduleResponse)
async def generate_schedule(request: ScheduleRequest):
    """
    Generates a new shift schedule based on the provided personnel and configuration.
    """
    solver = ScheduleSolver(request)
    solution = solver.solve()

    if solution:
        # The solver returns a dict of date strings to Shift objects.
        # We need to wrap it in the ScheduleResponse model.
        return ScheduleResponse(schedule=solution)
    
    raise HTTPException(
        status_code=409,
        detail="No optimal solution found within the time limit. Consider adjusting constraints.",
    )
