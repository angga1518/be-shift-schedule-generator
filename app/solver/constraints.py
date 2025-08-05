from __future__ import annotations
from typing import TYPE_CHECKING
from ..core.config import get_day_type, SHIFT_TYPES, DayTypes

if TYPE_CHECKING:
    from .schedule_solver import ScheduleSolver

def add_all_constraints(solver: ScheduleSolver):
    """
    Adds all scheduling constraints to the CP-SAT model.
    """
    _add_daily_staffing_constraints(solver)
    _add_shift_assignment_constraints(solver)
    _add_leave_constraints(solver)
    _add_personnel_role_constraints(solver)
    _add_critical_scheduling_rules(solver)


def _add_daily_staffing_constraints(solver: ScheduleSolver):
    """
    Ensures each shift on each day has the required number of personnel.
    """
    shift_requirements = {
        DayTypes.WEEKDAY: {"P": 1, "S": 2, "M": 2},
        DayTypes.WEEKEND_HOLIDAY: {"P": 2, "S": 2, "M": 3}
    }

    for d_idx, d_date in enumerate(solver.dates):
        day_type = get_day_type(d_date, solver.config.public_holidays)
        date_str = d_date.strftime('%Y-%m-%d')
        reqs = solver.config.special_dates.get(date_str, shift_requirements[day_type])

        for s_idx, s_type in enumerate(SHIFT_TYPES):
            required_count = reqs.get(s_type, 0)
            personnel_on_shift = [solver.shifts[(p_id, d_idx, s_idx)] for p_id in solver.personnel]
            solver.model.Add(sum(personnel_on_shift) == required_count)


def _add_shift_assignment_constraints(solver: ScheduleSolver):
    """
    Adds constraints related to how shifts can be assigned.
    - A person can work at most one shift per day.
    - A person cannot work more than the max number of night shifts.
    """
    night_shift_idx = SHIFT_TYPES.index("M")
    for p_id in solver.personnel:
        # At most one shift per day
        for d_idx in range(solver.num_days):
            shifts_on_day = [solver.shifts[(p_id, d_idx, s_idx)] for s_idx in range(solver.num_shifts)]
            solver.model.Add(sum(shifts_on_day) <= 1)

        # Max night shifts per month
        total_night_shifts = [solver.shifts[(p_id, d_idx, night_shift_idx)] for d_idx in range(solver.num_days)]
        solver.model.Add(sum(total_night_shifts) <= solver.config.max_night_shifts)


def _add_leave_constraints(solver: ScheduleSolver):
    """
    Ensures that personnel on any form of leave are not assigned shifts.
    """
    for p_id, person in solver.personnel.items():
        all_leaves = (person.requested_leaves + 
                      person.extra_leaves + 
                      person.annual_leaves)
        
        for day_of_month in all_leaves:
            d_idx = day_of_month - 1
            if 0 <= d_idx < solver.num_days:
                for s_idx in range(solver.num_shifts):
                    solver.model.Add(solver.shifts[(p_id, d_idx, s_idx)] == 0)


def _add_personnel_role_constraints(solver: ScheduleSolver):
    """
    Applies rules based on personnel roles.
    - 'non_shift' can only work Morning (P) shifts on weekdays.
    """
    for p_id, person in solver.personnel.items():
        if person.role == "non_shift":
            for d_idx, d_date in enumerate(solver.dates):
                day_type = get_day_type(d_date, solver.config.public_holidays)
                
                if day_type == DayTypes.WEEKEND_HOLIDAY:
                    for s_idx in range(solver.num_shifts):
                        solver.model.Add(solver.shifts[(p_id, d_idx, s_idx)] == 0)
                else: # Weekday
                    for s_idx, s_type in enumerate(SHIFT_TYPES):
                        if s_type != "P":
                            solver.model.Add(solver.shifts[(p_id, d_idx, s_idx)] == 0)


def _add_critical_scheduling_rules(solver: ScheduleSolver):
    """
    Adds complex rules like shift sequences, consecutive work limits,
    and mandatory post-night-shift leaves.
    """
    p_idx, s_idx, m_idx = [SHIFT_TYPES.index(s) for s in ["P", "S", "M"]]

    for p_id in solver.personnel:
        for d_idx in range(solver.num_days - 1):
            # Shift sequence rules
            # M -> M or L (not P or S)
            solver.model.AddImplication(solver.shifts[(p_id, d_idx, m_idx)], solver.shifts[(p_id, d_idx + 1, p_idx)].Not())
            solver.model.AddImplication(solver.shifts[(p_id, d_idx, m_idx)], solver.shifts[(p_id, d_idx + 1, s_idx)].Not())
            # S -> S, M, or L (not P)
            solver.model.AddImplication(solver.shifts[(p_id, d_idx, s_idx)], solver.shifts[(p_id, d_idx + 1, p_idx)].Not())

        # Consecutive shift limits
        for d_idx in range(solver.num_days - 2):
            # Max 2 consecutive nights
            solver.model.AddBoolOr([
                solver.shifts[(p_id, d_idx, m_idx)].Not(), 
                solver.shifts[(p_id, d_idx + 1, m_idx)].Not(), 
                solver.shifts[(p_id, d_idx + 2, m_idx)].Not()
            ])
        
        for d_idx in range(solver.num_days - 5):
            # Max 5 consecutive workdays
            work_days = [sum(solver.shifts[(p_id, d, s)] for s in range(solver.num_shifts)) for d in range(d_idx, d_idx + 6)]
            solver.model.Add(sum(work_days) <= 5)

        # Mandatory leave rules
        for d_idx in range(solver.num_days - 2):
            # After 2 consecutive nights -> 2 days leave
            is_mm = solver.model.NewBoolVar(f'p{p_id}_d{d_idx}_is_mm')
            solver.model.AddBoolAnd([
                solver.shifts[(p_id, d_idx, m_idx)],
                solver.shifts[(p_id, d_idx + 1, m_idx)]
            ]).OnlyEnforceIf(is_mm)
            
            if d_idx + 3 < solver.num_days:
                solver.model.Add(sum(solver.shifts[(p_id, d_idx + 2, s)] for s in range(solver.num_shifts)) == 0).OnlyEnforceIf(is_mm)
                solver.model.Add(sum(solver.shifts[(p_id, d_idx + 3, s)] for s in range(solver.num_shifts)) == 0).OnlyEnforceIf(is_mm)

        for d_idx in range(solver.num_days - 1):
            # After 1 night shift -> 1 day leave
            is_m = solver.model.NewBoolVar(f'p{p_id}_d{d_idx}_is_m')
            not_mm_before = solver.model.NewBoolVar(f'p{p_id}_d{d_idx}_not_mm_before')
            if d_idx > 0:
                solver.model.Add(solver.shifts[(p_id, d_idx - 1, m_idx)] == 0).OnlyEnforceIf(not_mm_before)
            else:
                solver.model.Add(not_mm_before == 1)

            solver.model.AddBoolAnd([
                solver.shifts[(p_id, d_idx, m_idx)],
                not_mm_before
            ]).OnlyEnforceIf(is_m)
            
            solver.model.Add(sum(solver.shifts[(p_id, d_idx + 1, s)] for s in range(solver.num_shifts)) == 0).OnlyEnforceIf(is_m)