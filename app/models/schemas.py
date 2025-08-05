from pydantic import BaseModel
from typing import List, Dict, Optional

class Personnel(BaseModel):
    id: int
    name: str
    role: str
    requested_leaves: List[int] = []
    extra_leaves: List[int] = []
    annual_leaves: List[int] = []

class ScheduleConfig(BaseModel):
    month: str
    public_holidays: List[int]
    max_night_shifts: int
    special_dates: Dict[str, Dict[str, int]] = {}

class ScheduleRequest(BaseModel):
    personnel: List[Personnel]
    config: ScheduleConfig

class Shift(BaseModel):
    P: List[int] = []
    S: List[int] = []
    M: List[int] = []

class ScheduleResponse(BaseModel):
    schedule: Dict[str, Shift]
