# Medical Shift Schedule Generator - Development Plan

This document outlines the development plan for the medical shift scheduling application. The project will use Python with Google OR-Tools for the core scheduling logic and FastAPI to expose it as an API.

---

## Phase 1: Project Setup & Initial Configuration

- [ ] **Initialize Python Environment**:
    - [ ] Create a virtual environment (e.g., `python -m venv venv`).
    - [ ] Activate the environment (`source venv/bin/activate`).
- [ ] **Install Dependencies**:
    - [ ] Install FastAPI: `pip install fastapi`.
    - [ ] Install Uvicorn server: `pip install "uvicorn[standard]"`.
    - [ ] Install Google OR-Tools: `pip install ortools`.
    - [ ] Install Pydantic for data modeling (comes with FastAPI).
- [ ] **Establish Project Structure**:
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
- [ ] **Create `requirements.txt`**:
    - [ ] Freeze dependencies: `pip freeze > requirements.txt`.
- [ ] **Setup `.gitignore`**:
    - [ ] Add common Python ignores (`venv/`, `__pycache__/`, `.pyc`).

---

## Phase 2: Data Modeling (`app/models/schemas.py`)

- [ ] **Define Input Models**:
    - [ ] Create `Personnel` Pydantic model (`id`, `name`, `role`, `requested_leaves`, `extra_leaves`, `annual_leaves`).
    - [ ] Create `ScheduleConfig` Pydantic model (`month`, `public_holidays`, `max_night_shifts`, `special_dates`).
    - [ ] Create main `ScheduleRequest` model to encapsulate all input data.
- [ ] **Define Output Models**:
    - [ ] Create `Shift` model (`P`, `S`, `M` fields, each a list of personnel IDs).
    - [ ] Create `ScheduleResponse` model, which is a dictionary mapping dates (strings) to `Shift` objects, to match the required JSON output.
- [ ] **Date & Holiday Logic (`app/core/config.py`)**:
    - [ ] Implement logic to determine weekdays, weekends, and holidays for the given month (2025-09).
    - [ ] Store shift types (P, S, M) and other constants.

---

## Phase 3: OR-Tools Solver Implementation (`app/solver/schedule_solver.py`)

- [ ] **Initialize Solver Class**:
    - [ ] Create a `ScheduleSolver` class that takes `ScheduleRequest` data as input.
    - [ ] Initialize the `CpModel` from `ortools.sat.python.cp_model`.
- [ ] **Define Solver Variables**:
    - [ ] Create a 3D dictionary of boolean variables: `shifts[(person_id, day, shift_type)]`.
- [ ] **Implement Core Constraints**:
    - [ ] **Daily Staffing:** Enforce the exact number of personnel required for each shift (P, S, M) based on day type (weekday, weekend, holiday, special date).
    - [ ] **No Double Shifts:** A person can work at most one shift per day.
    - [ ] **Leave Enforcement:** A person on any type of leave (L, LT, CT) cannot be assigned any shift on that day.
    - [ ] **Personnel Role Rules:**
        - [ ] `non_shift` personnel can only be assigned to Morning (P) shifts on non-holiday weekdays.
- [ ] **Implement Shift Sequence & Consecutive Work Rules**:
    - [ ] **Invalid Transitions:**
        - [ ] After a Night shift (M), the next day can only be another Night shift (M) or Leave (L).
        - [ ] After an Evening shift (S), the next day cannot be a Morning shift (P).
    - [ ] **Consecutive Shift Limits:**
        - [ ] A person cannot work more than 2 consecutive Night shifts.
        - [ ] A person cannot work more than 5 consecutive days (any shift combination).
- [ ] **Implement Mandatory Leave Rules**:
    - [ ] **Post-Night Shift Leave:**
        - [ ] Add constraint: 1 Night shift (M) must be followed by 1 mandatory leave day (L).
        - [ ] Add constraint: 2 consecutive Night shifts (MM) must be followed by 2 mandatory leave days (LL).
    - [ ] **Leave Priority:** Ensure that pre-requested leaves (L/LT/CT) take precedence over mandatory post-night leaves if they overlap.
- [ ] **Implement Global Constraints**:
    - [ ] **Monthly Night Shift Limit:** A person cannot work more than the `max_night_shifts` (9) in the month.
- [ ] **Define Objective Function (Workload Balancing)**:
    - [ ] Add an objective to distribute the total number of shifts as evenly as possible among all "shift" personnel.
    - [ ] (Optional) Add a secondary objective to minimize the number of `non_shift` personnel used.
- [ ] **Develop Solver Execution Logic**:
    - [ ] Create a `solve()` method that runs the `CpSolver`.
    - [ ] Implement logic to handle solver status (`OPTIMAL`, `FEASIBLE`, `INFEASIBLE`).
    - [ ] Create a solution printer/formatter that processes the solver's variable values and transforms them into the required JSON output format.

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
