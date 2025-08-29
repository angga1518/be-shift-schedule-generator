#!/usr/bin/env python3
"""
Test script to verify the new features:
1. INFEASIBLE handling - should return solution even when constraints are violated
2. max_non_shift parameter - should limit non-shift personnel usage
"""

from app.models.schemas import ScheduleRequest, Personnel, ScheduleConfig
from app.solver.schedule_solver import ScheduleSolver

def test_max_non_shift_parameter():
    """Test the max_non_shift parameter functionality - limits total working days per non-shift personnel"""
    print("Testing max_non_shift parameter (total working days limit)...")

    personnel = [
        Personnel(id=1, name="Shift Worker 1", role="shift"),
        Personnel(id=2, name="Shift Worker 2", role="shift"),
        Personnel(id=3, name="Shift Worker 3", role="shift"),
        Personnel(id=4, name="Shift Worker 4", role="shift"),
        Personnel(id=5, name="Non-Shift Worker", role="non_shift"),  # Only 1 non-shift worker
    ]

    # Test with max_non_shift = 2 (should limit non-shift worker to maximum 2 working days total)
    config = ScheduleConfig(
        month="2025-09",
        public_holidays=[17],
        max_night_shifts=9,
        max_non_shift=2  # Non-shift worker can work maximum 2 days total
    )

    request = ScheduleRequest(personnel=personnel, config=config)
    solver = ScheduleSolver(request)

    print("Solving with max_non_shift=2 (non-shift can work max 2 days total)...")
    solution = solver.solve()

    if solution:
        print("✅ Solution found!")
        # Count total working days for the non-shift worker (id=5)
        non_shift_id = 5
        working_days = 0

        for date, shifts in solution.items():
            if non_shift_id in shifts.P:  # Non-shift workers only work P shifts
                working_days += 1
                print(f"✅ {date}: Non-shift worker working (day {working_days})")
            else:
                print(f"   {date}: Non-shift worker not working")

        if working_days > 2:
            print(f"❌ Violation: Non-shift worker worked {working_days} days (max allowed: 2)")
        else:
            print(f"✅ Non-shift worker worked {working_days} days (within limit of 2)")
    else:
        print("❌ No solution found")

def test_infeasible_handling():
    """Test INFEASIBLE handling - should return solution even with violations"""
    print("\nTesting INFEASIBLE handling...")

    # Create a scenario that's likely to be infeasible
    personnel = [
        Personnel(id=1, name="Worker 1", role="shift", requested_leaves=list(range(1, 31))),  # All days off
        Personnel(id=2, name="Worker 2", role="shift", requested_leaves=list(range(1, 31))),  # All days off
    ]

    config = ScheduleConfig(
        month="2025-09",
        public_holidays=[17],
        max_night_shifts=9
    )

    request = ScheduleRequest(personnel=personnel, config=config)
    solver = ScheduleSolver(request)

    print("Solving with all personnel on leave (should be infeasible)...")
    solution = solver.solve()

    if solution:
        print("✅ Solution returned even though constraints are violated!")
        print("This demonstrates the new INFEASIBLE handling feature.")
    else:
        print("❌ No solution returned")

if __name__ == "__main__":
    test_max_non_shift_parameter()
    test_infeasible_handling()
    print("\n🎉 Test completed!")