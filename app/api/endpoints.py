from fastapi import APIRouter, HTTPException
from ..models.schemas import ScheduleRequest, ScheduleResponse, Shift
from ..solver.schedule_solver import ScheduleSolver

router = APIRouter()

@router.post("/generate-schedule", response_model=ScheduleResponse)
async def generate_schedule(request: ScheduleRequest):
    """
    Generates a new shift schedule based on the provided personnel and configuration.
    """
    try:
        solver = ScheduleSolver(request)
        solution = solver.solve()

        if solution:
            # The solver returns a dict of date strings to Shift objects.
            # We need to wrap it in the ScheduleResponse model.
            return ScheduleResponse(schedule=solution)

        raise HTTPException(
            status_code=409,
            detail="No solution found within the time limit. Consider adjusting constraints.",
        )
    
    except ValueError as e:
        error_message = str(e)

        if "MODEL_INVALID" in error_message:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "MODEL_INVALID",
                    "message": "There is an error in the scheduling model formulation.",
                    "suggestions": ["Contact system administrator"]
                }
            )
        elif "UNKNOWN" in error_message:
            raise HTTPException(
                status_code=408,
                detail={
                    "error": "TIMEOUT",
                    "message": "Unable to find a solution within the time limit.",
                    "suggestions": [
                        "Try the request again",
                        "Reduce complexity by adjusting leave requests",
                        "Contact administrator if problem persists"
                    ]
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "SOLVER_ERROR",
                    "message": f"An unexpected error occurred: {error_message}",
                    "suggestions": ["Contact system administrator"]
                }
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "INTERNAL_ERROR",
                "message": f"An unexpected system error occurred: {str(e)}",
                "suggestions": ["Contact system administrator"]
            }
        )
