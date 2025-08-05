import calendar
from datetime import date, timedelta
from typing import List


# --- Shift Types ---
SHIFT_TYPES = ["P", "S", "M"]

# --- Date & Holiday Logic ---

def get_days_in_month(year_month: str) -> List[date]:
    """Returns a list of all dates in the given month."""
    year, month = map(int, year_month.split('-'))
    num_days = calendar.monthrange(year, month)[1]
    return [date(year, month, day) for day in range(1, num_days + 1)]

def is_weekend(d: date) -> bool:
    """Checks if a date is a weekend (Saturday or Sunday)."""
    return d.weekday() >= 5  # Monday is 0 and Sunday is 6

def get_day_type(d: date, public_holidays: List[int]) -> str:
    """Determines if a day is a weekday, weekend, or holiday."""
    if d.day in public_holidays or is_weekend(d):
        return "weekend_holiday"
    return "weekday"

class DayTypes:
    WEEKDAY = "weekday"
    WEEKEND_HOLIDAY = "weekend_holiday"

