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

        # Mandatory leave rules - Improved based on TypeScript logic
        _add_mandatory_leave_constraints(solver, p_id, m_idx)


def _add_mandatory_leave_constraints(solver: ScheduleSolver, p_id: int, m_idx: int):
    """
    Implements mandatory leave rules with simplified logic:
    - After single night shift (M not preceded/followed by M): 1 day mandatory leave
    - After 2 consecutive night shifts (MM): 2 days mandatory leave
    """
    # Get person's requested leaves to avoid conflicts
    person = solver.personnel[p_id]
    all_requested_leaves = set(person.requested_leaves + person.extra_leaves + person.annual_leaves)
    
    # Single night shift rule
    for d_idx in range(solver.num_days - 1):
        if d_idx + 1 < solver.num_days:
            # Single M: M today AND (not M yesterday OR first day) AND not M tomorrow
            is_single_m = solver.model.NewBoolVar(f'single_m_{p_id}_{d_idx}')
            
            # Conditions for single night
            conditions = [solver.shifts[(p_id, d_idx, m_idx)]]  # Today is M
            if d_idx > 0:
                conditions.append(solver.shifts[(p_id, d_idx - 1, m_idx)].Not())  # Yesterday not M
            conditions.append(solver.shifts[(p_id, d_idx + 1, m_idx)].Not())  # Tomorrow not M
            
            solver.model.AddBoolAnd(conditions).OnlyEnforceIf(is_single_m)
            solver.model.AddBoolOr([cond.Not() for cond in conditions]).OnlyEnforceIf(is_single_m.Not())
            
            # If single M and tomorrow not already on requested leave, tomorrow must be leave
            tomorrow_day = d_idx + 2  # Convert to 1-indexed day
            if tomorrow_day not in all_requested_leaves and d_idx + 1 < solver.num_days:
                for s_idx in range(solver.num_shifts):
                    solver.model.AddImplication(is_single_m, solver.shifts[(p_id, d_idx + 1, s_idx)].Not())
    
    # Two consecutive nights rule
    for d_idx in range(solver.num_days - 1):
        if d_idx + 2 < solver.num_days:  # Need at least 2 days after for mandatory leave
            # Two consecutive M: M today AND M tomorrow
            consecutive_m = solver.model.NewBoolVar(f'consecutive_m_{p_id}_{d_idx}')
            
            solver.model.AddBoolAnd([
                solver.shifts[(p_id, d_idx, m_idx)],     # Today is M
                solver.shifts[(p_id, d_idx + 1, m_idx)]  # Tomorrow is M
            ]).OnlyEnforceIf(consecutive_m)
            
            solver.model.AddBoolOr([
                solver.shifts[(p_id, d_idx, m_idx)].Not(),     # Today not M OR
                solver.shifts[(p_id, d_idx + 1, m_idx)].Not()  # Tomorrow not M
            ]).OnlyEnforceIf(consecutive_m.Not())
            
            # After MM, next 2 days must be leave (if not already on requested leave)
            for offset in [2, 3]:  # Day after MM and day after that
                leave_day_idx = d_idx + offset
                leave_day_num = leave_day_idx + 1  # Convert to 1-indexed day
                
                if (leave_day_idx < solver.num_days and 
                    leave_day_num not in all_requested_leaves):
                    # Enforce mandatory leave only if not already on requested leave
                    for s_idx in range(solver.num_shifts):
                        solver.model.AddImplication(consecutive_m, solver.shifts[(p_id, leave_day_idx, s_idx)].Not())