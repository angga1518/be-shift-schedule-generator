# Medical Shift Schedule Generator - Development Plan

This document outlines the development plan for the medical shift scheduling application. The project will use Python with Google OR-Tools for the core scheduling logic and FastAPI to expose it as an API.

---

## Phase 1: Project Setup & Initial Configuration

- [x] **Initialize Python Environment**:
    - [x] Create a virtual environment (e.g., `python -m venv venv`).
    - [x] Activate the environment (`source venv/bin/activate`).
- [x] **Install Dependencies**:
    - [x] Install FastAPI: `pip install fastapi`.
    - [x] Install Uvicorn server: `pip install "uvicorn[standard]"`.
    - [x] Install Google OR-Tools: `pip install ortools`.
    - [x] Install Pydantic for data modeling (comes with FastAPI).
- [x] **Establish Project Structure**:
    ```
    /
    ├── app/
    │   ├── __init__.py
    │   ├── main.py         # FastAPI application
    │   ├── api/
    │   │   ├── __init__.py
    │   │   └── endpoints.py  # API endpoint logic
    │   ├── models/
    │   │   ├── __init__.py
    │   │   └── schemas.py    # Pydantic data models
    │   ├── solver/
    │   │   ├── __init__.py
    │   │   └── schedule_solver.py # Core OR-Tools logic
    │   └── core/
    │       ├── __init__.py
    │       └── config.py     # Application configuration
    ├── tests/
    │   ├── __init__.py
    │   └── test_scheduler.py # Unit and integration tests
    ├── .gitignore
    ├── requirements.txt
    └── README.md
    ```
- [x] **Create `requirements.txt`**:
    - [x] Freeze dependencies: `pip freeze > requirements.txt`.
- [x] **Setup `.gitignore`**:
    - [x] Add common Python ignores (`venv/`, `__pycache__/`, `.pyc`).

---

## Phase 2: Data Modeling (`app/models/schemas.py`)

- [x] **Define Input Models**:
    - [x] Create `Personnel` Pydantic model (`id`, `name`, `role`, `requested_leaves`, `extra_leaves`, `annual_leaves`).
    - [x] Create `ScheduleConfig` Pydantic model (`month`, `public_holidays`, `max_night_shifts`, `special_dates`).
    - [x] Create main `ScheduleRequest` model to encapsulate all input data.
- [x] **Define Output Models**:
    - [x] Create `Shift` model (`P`, `S`, `M` fields, each a list of personnel IDs).
    - [x] Create `ScheduleResponse` model, which is a dictionary mapping dates (strings) to `Shift` objects, to match the required JSON output.
- [x] **Date & Holiday Logic (`app/core/config.py`)**:
    - [x] Implement logic to determine weekdays, weekends, and holidays for the given month (2025-09).
    - [x] Store shift types (P, S, M) and other constants.

---

## Phase 3: OR-Tools Solver Implementation (`app/solver/schedule_solver.py`) - COMPLETED


## Personnel Role Rules

### Shift Personnel (role: "shift")
- Can work **all shift types**: P (Morning), S (Evening), M (Night)
- Can work **all days**: weekdays, weekends, and holidays
- **Primary workers** for all shifts

### Non-Shift Personnel (role: "non_shift") 
- Can **ONLY** work **Morning (P)** shifts
- Can **ONLY** work on **weekdays** (Monday-Friday, excluding holidays)
- **Cannot** work weekends or public holidays
- **Secondary priority**: Use as backup for Morning shifts only when shift personnel are unavailable

## Shift Requirements by Day Type

### Weekdays (Monday-Friday, excluding holidays)
- **P (Pagi/Morning)**: 1 person
- **S (Sore/Evening)**: 2 people  
- **M (Malam/Night)**: 2 people
- **Total**: 5 people per weekday

### Weekends & Holidays (Saturday, Sunday, Public Holidays)
- **P (Pagi/Morning)**: 2 people
- **S (Sore/Evening)**: 2 people
- **M (Malam/Night)**: 3 people  
- **Total**: 7 people per weekend/holiday

## Critical Scheduling Rules

### 1. Shift Sequence Rules (CRITICAL - MUST BE ENFORCED)
**Valid shift transitions for consecutive days:**
- **After Night (M)** → **Night (M)** or **Leave (L)** only
  - Cannot go M → P or M → S (invalid transitions)
- **After Afternoon (S)** → **S, M, or L** only  
  - Cannot go S → P (invalid transition)
- **After Morning (P)** → **P, S, M, or L** (all transitions allowed)

**Consecutive shift limits:**
- **Max 2 consecutive nights** → Must have leave after 2 consecutive M shifts
- **Max 5 consecutive workdays** → Must have leave after 5 consecutive work shifts (any combination of P/S/M)

### 2. Mandatory Leave Rules (CRITICAL - MUST BE ENFORCED)
- **After 1 night shift alone**: Person gets 1 day mandatory leave (L) the next day
- **After 2 consecutive night shifts**: Person gets 2 days mandatory leave (L) starting the next day
- **IMPORTANT**: Use L (not LT/CT) for mandatory post-night-shift leaves
- **Override priority**: If someone has pre-requested leave (L/LT/CT) on a day when they would get mandatory leave, the pre-requested leave takes priority
- **Examples**:
  - Day 5: Person works M → Day 6: Must have L (mandatory leave)
  - Day 8-9: Person works MM → Day 10-11: Must have LL (mandatory leaves)

### 3. Daily Staffing Requirements (MUST MATCH EXACTLY)
**Weekdays (Monday-Friday, excluding holidays)**:
- P (Morning): exactly 1 person
- S (Evening): exactly 2 people  
- M (Night): exactly 2 people
- Total: exactly 5 people per weekday

**Weekends & Holidays (Saturday, Sunday, Public Holidays)**:
- P (Morning): exactly 2 people
- S (Evening): exactly 2 people
- M (Night): exactly 3 people  
- Total: exactly 7 people per weekend/holiday

**Special Dates** (if any): Use the exact custom requirements specified

### 4. Shift Assignment Constraints
- **No double shifts**: A person cannot work multiple shifts on the same day
- **No shifts while on leave**: Person on any type of leave (L/LT/CT) cannot work shifts
- **Night shift limits**: Maximum 9 night shifts (M) per person per month
- **Workload balance**: Distribute shifts as evenly as possible among available personnel
- **Morning shift priority**: For weekday Morning (P) shifts, prioritize shift personnel first, use non_shift personnel only as backup when shift personnel are unavailable due to constraints

### 5. Leave Type Priorities
- **L (Requested Leave)**: Can be pre-requested OR mandatory post-night-shift leave
- **LT (Extra Leave)**: Pre-planned extra leave requests  
- **CT (Annual Leave)**: Pre-planned annual leave

### 6. Personnel Prioritization Strategy
- **Priority 1**: Personnel with MORE total leave requests should be scheduled first (while they're available)
- **Priority 2**: Balance workload among personnel with similar leave patterns
- **Rationale**: Use high-leave personnel during their available days since they'll be unavailable during leave periods

## Expected JSON Output Format

The output should be a JSON object where each date is a key, and each shift type contains an array of personnel IDs:

```json
{
  "2025-09-01": {
    "P": [1],
    "S": [2, 3], 
    "M": [4, 5]
  },
  "2025-09-02": {
    "P": [6],
    "S": [7, 8],
    "M": [9, 1]
  },
  // ... continue for all days in the month
}
```

## Validation Checklist

Before submitting your response, verify:
- [ ] All dates from first to last date of the month are included
- [ ] Each weekday has exactly 5 total assignments (P=1, S=2, M=2)
- [ ] Each weekend/holiday has exactly 7 total assignments (P=2, S=2, M=3)
- [ ] No person works shifts while on leave (L/LT/CT)
- [ ] Shift sequence rules are followed (M→M/L, S→S/M/L, P→P/S/M/L)
- [ ] No more than 2 consecutive night shifts per person
- [ ] No more than 5 consecutive work days per person
- [ ] Mandatory leave rules are applied after night shifts
- [ ] No person exceeds 9 night shifts
- [ ] Workload is reasonably balanced

---

## Phase 4: API Development (`app/main.py`, `app/api/endpoints.py`)

- [ ] **Create FastAPI Application (`app/main.py`)**:
    - [ ] Initialize the FastAPI app instance.
    - [ ] Include the router from `endpoints.py`.
    - [ ] Add a root endpoint `/` for a simple health check (e.g., `{"status": "ok"}`).
- [ ] **Develop API Endpoint (`app/api/endpoints.py`)**:
    - [ ] Create an API router.
    - [ ] Define a `/generate-schedule` endpoint that accepts `POST` requests.
    - [ ] The endpoint should take the `ScheduleRequest` Pydantic model as the request body.
    - [ ] Inside the endpoint:
        - [ ] Instantiate the `ScheduleSolver`.
        - [ ] Call the `solve()` method.
        - [ ] Return the `ScheduleResponse` with a `200 OK` status if a solution is found.
        - [ ] Return an appropriate HTTP error (e.g., `409 Conflict` or `400 Bad Request`) if no solution can be found, along with an error message.

---

## Phase 5: Testing (`tests/test_scheduler.py`)

- [ ] **Setup Testing Framework**:
    - [ ] Configure `pytest` to run the tests.
    - [ ] Install `httpx` for async testing of the FastAPI client.
- [ ] **Write Unit Tests**:
    - [ ] Test the date and holiday calculation logic.
    - [ ] Test the Pydantic data models with valid and invalid data.
- [ ] **Write Integration Tests**:
    - [ ] Create a test for the `/generate-schedule` endpoint using FastAPI's `TestClient`.
    - [ ] Use the exact data from `requirement.md` as the test payload.
    - [ ] In the test, programmatically validate the generated schedule against all the rules in the "Validation Checklist" from `requirement.md`.
        - [ ] Check daily staffing counts.
        - [ ] Verify shift sequence rules.
        - [ ] Check consecutive day limits.
        - [ ] Assert mandatory leaves are applied correctly.
        - [ ] Confirm no one exceeds the night shift limit.

---

## Phase 6: Documentation & Finalization

- [ ] **Write `README.md`**:
    - [ ] Add a project description.
    - [ ] Provide clear instructions on how to set up the virtual environment, install dependencies, and run the application.
    - [ ] Include an example `curl` command to use the `/generate-schedule` endpoint.
    - [ ] Explain the project structure.
- [ ] **Add Code Documentation**:
    - [ ] Add docstrings to all major classes and functions, explaining their purpose, arguments, and return values.
- [ ] **Final Review**:
    - [ ] Review the entire codebase for clarity, efficiency, and adherence to best practices.
    - [ ] Manually test the API one last time.