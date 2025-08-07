# Medical Shift Schedule Generator

## Overview

This project is a **medical shift scheduling application** built with Python, using **Google OR-Tools** for constraint programming and **FastAPI** for the API layer. It generates monthly shift schedules for medical personnel, ensuring all complex rules and constraints are satisfied.

## Features

- **Optimal monthly shift scheduling** for medical staff
- **Constraint-based solver** using Google OR-Tools
- **REST API** for schedule generation (`/api/generate-schedule`)
- **Personnel leave management** (requested, extra, annual, mandatory)
- **Role-based shift assignment** (shift/non-shift personnel)
- **Daily staffing requirements** (weekdays, weekends, holidays, special dates)
- **Enforcement of critical scheduling rules** (shift sequences, mandatory leaves, workload balance)
- **JSON output** for easy integration

## How It Works

1. **Input**: Send a POST request to `/api/generate-schedule` with personnel data and configuration.
2. **Processing**: The solver applies all constraints and generates a feasible schedule.
3. **Output**: Returns a JSON object mapping each date to assigned personnel for each shift.

## API Example

See `contoh curl.md` for a sample cURL request and expected JSON response.

## Project Structure

```
app/
  ├── main.py              # FastAPI app entry point
  ├── api/endpoints.py     # API route definitions
  ├── models/schemas.py    # Pydantic models for requests/responses
  ├── solver/              # OR-Tools solver and constraints
  └── core/config.py       # Date, shift, and config utilities
tests/
  └── test_scheduler.py    # Unit tests for schedule generation
requirement.md             # Full requirements and rules
TODO.MD                    # Development roadmap
README.md                  # Project documentation
requirements.txt           # Python dependencies
```

## Requirements

- Python 3.11+
- Google OR-Tools
- FastAPI
- Pydantic

Install dependencies:
```sh
pip install -r requirements.txt
```

## Usage

Start the API server:
```sh
uvicorn app.main:app --reload
```

Then POST your scheduling request to:
```
http://localhost:8000/api/generate-schedule
```

## Development

See `TODO.MD` for a step-by-step development plan. All scheduling rules and constraints are detailed in `requirement.md`.

---

Let me know if you want to add installation, contribution, or troubleshooting sections!
