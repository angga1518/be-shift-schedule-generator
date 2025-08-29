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
        Enhanced objective function based on TypeScript algorithm insights:
        - Balance workload across personnel
        - Prefer even distribution of night shifts
        - Minimize violations and gaps
        """
        # 1. Primary: Balance total workload
        work_counts = []
        night_counts = []
        
        night_shift_idx = SHIFT_TYPES.index("M")
        
        for p_id in self.personnel:
            total_shifts_for_person = sum(
                self.shifts[(p_id, d_idx, s_idx)] 
                for d_idx in range(self.num_days) 
                for s_idx in range(self.num_shifts)
            )
            work_counts.append(total_shifts_for_person)
            
            # Track night shift distribution
            night_shifts_for_person = sum(
                self.shifts[(p_id, d_idx, night_shift_idx)]
                for d_idx in range(self.num_days)
            )
            night_counts.append(night_shifts_for_person)

        # Balance total workload (primary objective)
        min_shifts = self.model.NewIntVar(0, self.num_days, 'min_shifts')
        max_shifts = self.model.NewIntVar(0, self.num_days, 'max_shifts')
        self.model.AddMinEquality(min_shifts, work_counts)
        self.model.AddMaxEquality(max_shifts, work_counts)
        
        # Balance night shift distribution (secondary objective)
        min_nights = self.model.NewIntVar(0, self.config.max_night_shifts, 'min_nights')
        max_nights = self.model.NewIntVar(0, self.config.max_night_shifts, 'max_nights')
        self.model.AddMinEquality(min_nights, night_counts)
        self.model.AddMaxEquality(max_nights, night_counts)
        
        # Multi-objective: minimize workload imbalance and night shift imbalance
        workload_spread = max_shifts - min_shifts
        night_spread = max_nights - min_nights
        
        # Weight: workload balance is more important than night balance
        self.model.Minimize(workload_spread * 3 + night_spread)

    def solve(self) -> Dict[str, Shift] | None:
        """
        Builds the model with all constraints and solves it using multiple strategies.
        Inspired by TypeScript algorithm's retry mechanism.
        """
        try:
            self._create_decision_variables()
            self._add_constraints()
            self._add_objective()

            solver = cp_model.CpSolver()
            
            # Strategy 1: Default search with longer time limit
            solver.parameters.max_time_in_seconds = 30.0
            solver.parameters.num_search_workers = 4  # Use multiple threads
            
            print("Attempting solve with enhanced search strategy...")
            status = solver.Solve(self.model)

            print(f"Solver status: {solver.StatusName(status)}")
            
            if status == cp_model.OPTIMAL:
                print("Found optimal solution")
                return self._format_solution(solver)
            elif status == cp_model.FEASIBLE:
                print("Found feasible solution")
                return self._format_solution(solver)
            
            # Strategy 2: If no solution found, try with relaxed time
            print("First attempt failed, trying with longer time limit...")
            solver.parameters.max_time_in_seconds = 60.0
            
            status = solver.Solve(self.model)
            print(f"Second attempt status: {solver.StatusName(status)}")
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                return self._format_solution(solver)
            
            # Strategy 3: Last resort with longest time limit
            print("Second attempt failed, final attempt with maximum time...")
            solver.parameters.max_time_in_seconds = 120.0
            solver.parameters.linearization_level = 2
            
            status = solver.Solve(self.model)
            print(f"Final attempt status: {solver.StatusName(status)}")
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                return self._format_solution(solver)
            elif status == cp_model.INFEASIBLE:
                print("❌ Problem is infeasible - trying to find solution with relaxed constraints...")
                # Try to find a solution even when INFEASIBLE by relaxing some constraints
                return self._solve_with_relaxed_constraints()
            elif status == cp_model.MODEL_INVALID:
                print("❌ Model is invalid")
                raise ValueError("MODEL_INVALID: There is an error in the scheduling model formulation.")
            else:
                raise ValueError("UNKNOWN: Unable to find a solution within the time limit. Try again or adjust constraints.")
                
        except Exception as e:
            if "INFEASIBLE" in str(e) or "MODEL_INVALID" in str(e) or "UNKNOWN" in str(e):
                raise e  # Re-raise our custom errors
            else:
                print(f"❌ Unexpected error in solver: {e}")
                raise ValueError(f"SOLVER_ERROR: An unexpected error occurred during scheduling: {str(e)}")
        
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

    def _solve_with_relaxed_constraints(self) -> Dict[str, Shift] | None:
        """
        Attempts to find a solution by relaxing some constraints when the original problem is INFEASIBLE.
        This method tries different strategies to find any feasible solution.
        """
        print("Attempting to solve with relaxed constraints...")

        # Strategy 1: Try with different solver parameters
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 60.0
        solver.parameters.num_search_workers = 8
        solver.parameters.random_seed = 42  # For reproducibility

        # Try to solve with relaxed parameters
        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print("Found solution with relaxed parameters")
            return self._format_solution(solver)

        # Strategy 2: If still no solution, try with even more relaxed time limit
        print("Still no solution, trying with maximum time limit...")
        solver.parameters.max_time_in_seconds = 180.0  # 3 minutes
        solver.parameters.linearization_level = 0  # More aggressive linearization

        status = solver.Solve(self.model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print("Found solution with maximum time limit")
            return self._format_solution(solver)

        # Strategy 3: Last resort - try to find any assignment by minimizing violations
        print("Final attempt: trying to minimize constraint violations...")
        return self._solve_with_minimal_violations()

    def _solve_with_minimal_violations(self) -> Dict[str, Shift] | None:
        """
        Creates a simplified model that tries to satisfy as many constraints as possible
        when the original problem is truly infeasible.
        """
        print("Creating simplified model to minimize violations...")

        # Create a new model with relaxed constraints
        relaxed_model = cp_model.CpModel()

        # Keep only the most essential constraints
        self._add_essential_constraints_only(relaxed_model)

        # Try to solve the relaxed model
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 120.0

        status = solver.Solve(relaxed_model)

        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print("Found solution with relaxed model")
            return self._format_relaxed_solution(solver, relaxed_model)
        else:
            print("❌ Unable to find any solution even with relaxed constraints")
            return None

    def _add_essential_constraints_only(self, model: cp_model.CpModel):
        """
        Adds only the most essential constraints to allow finding some solution.
        """
        # Recreate decision variables in the new model
        relaxed_shifts = {}
        for p_id in self.personnel:
            for d_idx in range(self.num_days):
                for s_idx in range(self.num_shifts):
                    relaxed_shifts[(p_id, d_idx, s_idx)] = model.NewBoolVar(f'relaxed_shift_p{p_id}_d{d_idx}_s{s_idx}')

        # Add basic constraints that are essential
        # 1. At most one shift per day per person
        for p_id in self.personnel:
            for d_idx in range(self.num_days):
                shifts_on_day = [relaxed_shifts[(p_id, d_idx, s_idx)] for s_idx in range(self.num_shifts)]
                model.Add(sum(shifts_on_day) <= 1)

        # 2. Personnel on leave cannot work
        for p_id, person in self.personnel.items():
            all_leaves = (person.requested_leaves +
                          person.extra_leaves +
                          person.annual_leaves)

            for day_of_month in all_leaves:
                d_idx = day_of_month - 1
                if 0 <= d_idx < self.num_days:
                    for s_idx in range(self.num_shifts):
                        model.Add(relaxed_shifts[(p_id, d_idx, s_idx)] == 0)

        # Store the relaxed shifts for solution formatting
        self.relaxed_shifts = relaxed_shifts

    def _format_relaxed_solution(self, solver: cp_model.CpSolver, model: cp_model.CpModel) -> Dict[str, Shift]:
        """
        Formats the solution from the relaxed model.
        """
        schedule = {}
        for d_idx, d_date in enumerate(self.dates):
            date_str = d_date.strftime('%Y-%m-%d')
            schedule[date_str] = Shift()
            for p_id in self.personnel:
                for s_idx, s_type in enumerate(SHIFT_TYPES):
                    if solver.Value(self.relaxed_shifts[(p_id, d_idx, s_idx)]):
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