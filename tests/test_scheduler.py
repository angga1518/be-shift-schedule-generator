import pytest
from fastapi.testclient import TestClient
from datetime import date

from app.main import app
from app.models.schemas import ScheduleRequest, Personnel, ScheduleConfig
from app.core.config import get_day_type, DayTypes

client = TestClient(app)

# --- Unit Tests ---

def test_get_day_type():
    """Tests the day type logic for weekdays, weekends, and holidays."""
    d_weekday = date(2025, 9, 1)  # A Monday
    d_weekend = date(2025, 9, 6)  # A Saturday
    public_holidays = [1, 15]
    
    assert get_day_type(d_weekday, public_holidays) == DayTypes.WEEKEND_HOLIDAY # It's a holiday
    assert get_day_type(date(2025, 9, 2), public_holidays) == DayTypes.WEEKDAY
    assert get_day_type(d_weekend, public_holidays) == DayTypes.WEEKEND_HOLIDAY

# --- Integration Test ---

@pytest.fixture
def test_payload() -> ScheduleRequest:
    """Provides a standard test payload for the API endpoint."""
    personnel = [
        Personnel(id=i, name=f"Person {i}", role="shift") for i in range(1, 11)
    ]
    personnel.append(Personnel(id=11, name="Non-Shift 1", role="non_shift"))
    
    config = ScheduleConfig(
        month="2025-09",
        public_holidays=[16], # Eid al-Fitr
        max_night_shifts=9,
    )
    return ScheduleRequest(personnel=personnel, config=config)

def test_generate_schedule_endpoint(test_payload: ScheduleRequest):
    """
    Tests the /generate-schedule endpoint, validating the entire scheduling process.
    """
    response = client.post("/api/generate-schedule", json=test_payload.model_dump())
    
    assert response.status_code == 200
    schedule_data = response.json()["schedule"]

    # --- Validation Checklist ---
    
    # 1. All dates are included
    assert len(schedule_data) == 30 # September 2025 has 30 days

    # 2. Daily staffing requirements
    public_holidays = test_payload.config.public_holidays
    for date_str, shifts in schedule_data.items():
        d = date.fromisoformat(date_str)
        day_type = get_day_type(d, public_holidays)
        
        if day_type == DayTypes.WEEKDAY:
            assert len(shifts["P"]) == 1
            assert len(shifts["S"]) == 2
            assert len(shifts["M"]) == 2
        else: # Weekend or Holiday
            assert len(shifts["P"]) == 2
            assert len(shifts["S"]) == 2
            assert len(shifts["M"]) == 3

    # 3. No shifts while on leave (tested implicitly by solver)
    # 4. Shift sequence rules (complex to validate here, primary test is solver logic)
    # 5. Consecutive day limits (complex to validate here)
    # 6. Mandatory leave rules (complex to validate here)
    
    # 7. Night shift limits
    night_shift_counts = {p.id: 0 for p in test_payload.personnel}
    for shifts in schedule_data.values():
        for p_id in shifts["M"]:
            night_shift_counts[p_id] += 1
    
    for count in night_shift_counts.values():
        assert count <= test_payload.config.max_night_shifts

    # 8. Workload balance (hard to assert a specific threshold)
    # We can at least check that all shift personnel have some shifts
    work_counts = {p.id: 0 for p in test_payload.personnel if p.role == 'shift'}
    for shifts in schedule_data.values():
        for shift_type in ["P", "S", "M"]:
            for p_id in shifts[shift_type]:
                if p_id in work_counts:
                    work_counts[p_id] += 1
    
    for p_id in work_counts:
        assert work_counts[p_id] > 0
