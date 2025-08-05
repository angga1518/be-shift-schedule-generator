from ortools.sat.python import cp_model
from ..models.schemas import ScheduleRequest, Shift
from ..core.config import get_days_in_month, get_day_type, SHIFT_TYPES
from typing import List, Dict, Tuple

from . import constraints

class ScheduleSolver:
    """
    A class to solve the medical shift scheduling problem using Google OR-Tools.
    """
    def __init__(self, request: ScheduleRequest):
        """
        Initializes the solver with the schedule request data.
        """
        self.request = request
        self.personnel = {p.id: p for p in self.request.personnel}
        self.config = self.request.config

        self.dates = get_days_in_month(self.config.month)
        self.num_days = len(self.dates)
        self.num_personnel = len(self.personnel)
        self.num_shifts = len(SHIFT_TYPES)

        self.model = cp_model.CpModel()
        self.shifts = {}  # Decision variables

    def _create_decision_variables(self):
        """
        Creates the main decision variables for the model.
        """
        for p_id in self.personnel:
            for d_idx in range(self.num_days):
                for s_idx in range(self.num_shifts):
                    self.shifts[(p_id, d_idx, s_idx)] = self.model.NewBoolVar(f'shift_p{p_id}_d{d_idx}_s{s_idx}')

    def _add_objective(self):
        """
        Adds the objective function to the model to balance the workload.
        """
        work_counts = []
        for p_id in self.personnel:
            total_shifts_for_person = sum(
                self.shifts[(p_id, d_idx, s_idx)] 
                for d_idx in range(self.num_days) 
                for s_idx in range(self.num_shifts)
            )
            work_counts.append(total_shifts_for_person)

        min_shifts = self.model.NewIntVar(0, self.num_days, 'min_shifts')
        max_shifts = self.model.NewIntVar(0, self.num_days, 'max_shifts')
        self.model.AddMinEquality(min_shifts, work_counts)
        self.model.AddMaxEquality(max_shifts, work_counts)
        
        self.model.Minimize(max_shifts - min_shifts)

    def solve(self) -> Dict[str, Shift] | None:
        """
        Builds the model with all constraints and solves it.
        """
        self._create_decision_variables()
        self._add_constraints()
        self._add_objective()

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60.0
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            return self._format_solution(solver)
        
        return None

    def _format_solution(self, solver: cp_model.CpSolver) -> Dict[str, Shift]:
        """
        Formats the solver's solution into the required response structure.
        """
        schedule = {}
        for d_idx, d_date in enumerate(self.dates):
            date_str = d_date.strftime('%Y-%m-%d')
            schedule[date_str] = Shift()
            for p_id in self.personnel:
                for s_idx, s_type in enumerate(SHIFT_TYPES):
                    if solver.Value(self.shifts[(p_id, d_idx, s_idx)]):
                        if s_type == "P":
                            schedule[date_str].P.append(p_id)
                        elif s_type == "S":
                            schedule[date_str].S.append(p_id)
                        elif s_type == "M":
                            schedule[date_str].M.append(p_id)
        return schedule

    def _add_constraints(self):
        """
        Adds all constraints to the model by calling the constraint module.
        """
        constraints.add_all_constraints(self)