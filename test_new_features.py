#!/usr/bin/env python3
"""
Test script to verify the new features:
1. INFEASIBLE handling - should return solution even when constraints are violated
2. max_non_shift parameter - should limit non-shift personnel usage
"""

from app.models.schemas import ScheduleRequest, Personnel, ScheduleConfig
from app.solver.schedule_solver import ScheduleSolver

def test_max_non_shift_parameter():
    """Test the max_non_shift parameter functionality"""
    print("Testing max_non_shift parameter...")

    personnel = [
        Personnel(id=1, name="Shift Worker 1", role="shift"),
        Personnel(id=2, name="Shift Worker 2", role="shift"),
        Personnel(id=3, name="Non-Shift Worker 1", role="non_shift"),
        Personnel(id=4, name="Non-Shift Worker 2", role="non_shift"),
        Personnel(id=5, name="Non-Shift Worker 3", role="non_shift"),
    ]

    # Test with max_non_shift = 1 (should limit to 1 non-shift worker per day)
    config = ScheduleConfig(
        month="2025-09",
        public_holidays=[17],
        max_night_shifts=9,
        max_non_shift=1  # Only allow 1 non-shift worker per day
    )

    request = ScheduleRequest(personnel=personnel, config=config)
    solver = ScheduleSolver(request)

    print("Solving with max_non_shift=1...")
    solution = solver.solve()

    if solution:
        print("✅ Solution found!")
        # Count non-shift workers per day
        for date, shifts in solution.items():
            non_shift_count = len(shifts.P)  # Non-shift workers only work P shifts
            if non_shift_count > 1:
                print(f"❌ Violation: {date} has {non_shift_count} non-shift workers (max allowed: 1)")
            else:
                print(f"✅ {date}: {non_shift_count} non-shift workers")
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