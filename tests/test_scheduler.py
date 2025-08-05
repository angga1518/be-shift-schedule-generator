import pytest
from fastapi.testclient import TestClient
from datetime import date

from app.main import app
from app.models.schemas import ScheduleRequest, Personnel, ScheduleConfig
from app.core.config import get_day_type, DayTypes, SHIFT_TYPES

client = TestClient(app)

# --- Unit Tests ---

def test_get_day_type():
    """Tests the day type logic for weekdays, weekends, and holidays."""
    d_weekday = date(2025, 9, 2)
    d_weekend = date(2025, 9, 6)
    d_holiday = date(2025, 9, 17)
    public_holidays = [17]
    
    assert get_day_type(d_weekday, public_holidays) == DayTypes.WEEKDAY
    assert get_day_type(d_weekend, public_holidays) == DayTypes.WEEKEND_HOLIDAY
    assert get_day_type(d_holiday, public_holidays) == DayTypes.WEEKEND_HOLIDAY

# --- Integration Test ---

@pytest.fixture
def test_payload() -> ScheduleRequest:
    """Provides a standard test payload based on dummydata.md."""
    personnel = [
        Personnel(id=1, name="Andi", role="shift", requested_leaves=[5]),
        Personnel(id=2, name="Budi", role="shift"),
        Personnel(id=3, name="Citra", role="shift", annual_leaves=[29]),
        Personnel(id=4, name="Dedi", role="shift"),
        Personnel(id=5, name="Eka", role="shift", requested_leaves=[15]),
        Personnel(id=6, name="Gita", role="shift"),
        Personnel(id=7, name="Hani", role="shift"),
        Personnel(id=8, name="Indra", role="shift", requested_leaves=[10]),
        Personnel(id=9, name="Joko", role="shift"),
        Personnel(id=10, name="Fani", role="non_shift"),
    ]
    
    config = ScheduleConfig(
        month="2025-09",
        public_holidays=[17],
        max_night_shifts=9,
        special_dates={"2025-09-20": {"P": 1, "S": 1, "M": 3}}
    )
    return ScheduleRequest(personnel=personnel, config=config)

def test_generate_schedule_endpoint(test_payload: ScheduleRequest):
    """
    Tests the /generate-schedule endpoint with dummy data and validates all rules.
    """
    response = client.post("/api/generate-schedule", json=test_payload.model_dump())
    assert response.status_code == 200
    schedule_data = response.json()["schedule"]

    # --- Debug: Print the schedule ---
    print("\n=== GENERATED SCHEDULE ===")
    for date_str in sorted(schedule_data.keys()):
        shifts = schedule_data[date_str]
        print(f"{date_str}: P={shifts['P']}, S={shifts['S']}, M={shifts['M']}")

    # --- Validation Setup ---
    personnel_schedules = {p.id: {} for p in test_payload.personnel}
    for date_str, shifts in schedule_data.items():
        for shift_type, p_ids in shifts.items():
            for p_id in p_ids:
                personnel_schedules[p_id][date_str] = shift_type

    # --- Debug: Print personnel schedules ---
    print("\n=== PERSONNEL SCHEDULES ===")
    for p_id, schedule in personnel_schedules.items():
        if schedule:  # Only print if person has any shifts
            days = []
            for day_num in range(1, 31):
                date_str = f"2025-09-{day_num:02d}"
                shift = schedule.get(date_str, '_')
                days.append(shift)
            print(f"Person {p_id}: {''.join(days)}")

    # --- Rule Validations ---
    _validate_all_dates_present(schedule_data)
    _validate_personnel_ids(schedule_data, test_payload.personnel)
    _validate_staffing_requirements(schedule_data, test_payload.config)
    _validate_leaves(schedule_data, test_payload.personnel)
    _validate_critical_rules(personnel_schedules)
    _validate_max_night_shifts(personnel_schedules, test_payload.config.max_night_shifts)

# --- Helper Validation Functions ---

def _validate_all_dates_present(schedule):
    assert len(schedule) == 30

def _validate_personnel_ids(schedule, personnel_list):
    valid_ids = {p.id for p in personnel_list}
    for shifts in schedule.values():
        for shift_list in shifts.values():
            for p_id in shift_list:
                assert p_id in valid_ids

def _validate_staffing_requirements(schedule, config):
    for date_str, shifts in schedule.items():
        d = date.fromisoformat(date_str)
        if date_str in config.special_dates:
            reqs = config.special_dates[date_str]
            assert len(shifts["P"]) == reqs.get("P", 0)
            assert len(shifts["S"]) == reqs.get("S", 0)
            assert len(shifts["M"]) == reqs.get("M", 0)
        else:
            day_type = get_day_type(d, config.public_holidays)
            if day_type == DayTypes.WEEKDAY:
                assert len(shifts["P"]) == 1 and len(shifts["S"]) == 2 and len(shifts["M"]) == 2
            else:
                assert len(shifts["P"]) == 2 and len(shifts["S"]) == 2 and len(shifts["M"]) == 3

def _validate_leaves(schedule, personnel_list):
    for p in personnel_list:
        all_leaves = p.requested_leaves + p.extra_leaves + p.annual_leaves
        for day_num in all_leaves:
            date_str = f"2025-09-{day_num:02d}"
            if date_str in schedule:
                for shift_type in SHIFT_TYPES:
                    assert p.id not in schedule[date_str][shift_type]

def _validate_critical_rules(personnel_schedules):
    for p_id, schedule in personnel_schedules.items():
        for day_num in range(1, 31):
            date_str = f"2025-09-{day_num:02d}"
            shift_today = schedule.get(date_str)

            if shift_today:
                # Shift Sequence
                if day_num < 30:
                    shift_tomorrow = schedule.get(f"2025-09-{day_num + 1:02d}")
                    if shift_today == "M": assert shift_tomorrow in [None, "M"]
                    if shift_today == "S": assert shift_tomorrow != "P"

                # Mandatory Leave
                if shift_today == 'M':
                    # Check if this is a single night shift (not preceded by M and not followed by M)
                    is_single_m = (schedule.get(f"2025-09-{day_num-1:02d}") != 'M' and 
                                   schedule.get(f"2025-09-{day_num+1:02d}") != 'M')
                    if is_single_m and day_num < 30:
                        # After single night shift, next day must be leave
                        assert f"2025-09-{day_num+1:02d}" not in schedule

                    # Check if this is the end of 2 consecutive night shifts
                    is_double_m_end = (schedule.get(f"2025-09-{day_num-1:02d}") == 'M' and
                                       schedule.get(f"2025-09-{day_num+1:02d}") != 'M')
                    if is_double_m_end and day_num < 29:
                        # After 2 consecutive nights, next 2 days must be leave
                        assert f"2025-09-{day_num+1:02d}" not in schedule
                        assert f"2025-09-{day_num+2:02d}" not in schedule
        
        # Consecutive Days
        work_stretches = "".join(['W' if f"2025-09-{d:02d}" in schedule else '_' for d in range(1, 31)])
        assert "WWWWWW" not in work_stretches
        
        night_stretches = "".join(['M' if schedule.get(f"2025-09-{d:02d}") == 'M' else '_' for d in range(1, 31)])
        assert "MMM" not in night_stretches

def _validate_max_night_shifts(personnel_schedules, max_nights):
    for p_id, schedule in personnel_schedules.items():
        night_shifts = sum(1 for shift in schedule.values() if shift == "M")
        assert night_shifts <= max_nights