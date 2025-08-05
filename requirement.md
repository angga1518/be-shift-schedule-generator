"You are an expert Python developer specializing in Google OR-Tools and API design. Your task is to act as a project manager and create a comprehensive development plan in a markdown file named `TODO.MD`.

This plan will guide the development of a complex medical shift scheduling application. The application will be a Python script that uses Google OR-Tools to solve the scheduling problem and exposes the functionality through a FastAPI endpoint.

Read the detailed requirements provided below. Based on these requirements, generate a `TODO.MD` file with a detailed, step-by-step checklist. The checklist should be broken down into logical phases (e.g., Setup, Data Modeling, Solver Implementation, API, Testing). Each item should be a concrete, actionable task for a developer (or an AI assistant like yourself) to execute. The goal is to create a roadmap so clear that we can build the entire application by following this checklist.

# Shift Schedule Generation Task



You are an expert scheduler tasked with creating a monthly shift schedule for medical personnel. Please generate a valid JSON schedule that follows all the rules and constraints outlined below.



## Configuration

- **Month**: 2025-09 (30 days)

- **Public Holidays**: 17

- **Max Night Shifts per person**: 9

- **Max Default Leaves per person**: 10



## Special Dates

- 2025-09-20: P=1, S=1, M=3



## Personnel Information

**dr. LARAS W** (ID: 1) - Role: shift

  - Requested Leaves (L): [None]

  - Extra Leaves (LT): [None]  

  - Annual Leaves (CT): [None]

  - Total leave days: 0



**dr. SITI AISYAH** (ID: 2) - Role: shift

  - Requested Leaves (L): [6, 7]

  - Extra Leaves (LT): [12, 13, 14, 27, 28]  

  - Annual Leaves (CT): [None]

  - Total leave days: 7



**dr. RABIATUL H** (ID: 3) - Role: shift

  - Requested Leaves (L): [None]

  - Extra Leaves (LT): [None]  

  - Annual Leaves (CT): [None]

  - Total leave days: 0



**dr. ADIE K** (ID: 4) - Role: shift

  - Requested Leaves (L): [None]

  - Extra Leaves (LT): [25, 26, 27]  

  - Annual Leaves (CT): [None]

  - Total leave days: 3



**dr. LOKOT** (ID: 5) - Role: shift

  - Requested Leaves (L): [9, 10]

  - Extra Leaves (LT): [11, 12, 13, 14, 15]  

  - Annual Leaves (CT): [None]

  - Total leave days: 7



**dr. VENEZIA A** (ID: 6) - Role: shift

  - Requested Leaves (L): [16, 17]

  - Extra Leaves (LT): [18, 19]  

  - Annual Leaves (CT): [None]

  - Total leave days: 4



**dr. ANINDA** (ID: 7) - Role: shift

  - Requested Leaves (L): [None]

  - Extra Leaves (LT): [20, 21, 22]  

  - Annual Leaves (CT): [None]

  - Total leave days: 3



**dr. GRACYA** (ID: 8) - Role: shift

  - Requested Leaves (L): [4, 5, 17, 18]

  - Extra Leaves (LT): [6]  

  - Annual Leaves (CT): [None]

  - Total leave days: 5



**dr. ANISA A** (ID: 9) - Role: shift

  - Requested Leaves (L): [21, 22]

  - Extra Leaves (LT): [1, 2, 3, 4, 23, 24]  

  - Annual Leaves (CT): [None]

  - Total leave days: 8



**NON_SHIFT_1** (ID: 10) - Role: non_shift

  - Requested Leaves (L): [None]

  - Extra Leaves (LT): [None]  

  - Annual Leaves (CT): [None]

  - Total leave days: 0



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

- [ ] All dates from 2025-09-01 to 2025-09-30 are included

- [ ] Each weekday has exactly 5 total assignments (P=1, S=2, M=2)

- [ ] Each weekend/holiday has exactly 7 total assignments (P=2, S=2, M=3)

- [ ] All personnel IDs are valid: 1, 2, 3, 4, 5, 6, 7, 8, 9

- [ ] No person works shifts while on leave (L/LT/CT)

- [ ] Shift sequence rules are followed (M→M/L, S→S/M/L, P→P/S/M/L)

- [ ] No more than 2 consecutive night shifts per person

- [ ] No more than 5 consecutive work days per person

- [ ] Mandatory leave rules are applied after night shifts

- [ ] No person exceeds 9 night shifts

- [ ] Workload is reasonably balanced

- [ ] Requested leaves (L) override mandatory leaves (LT/CT) when they conflict



## Instructions

1. **Start with leave assignment**: First assign all requested leaves (L, LT, CT) for all personnel

2. **Apply prioritization**: Prioritize personnel with more total leave days for shift assignments

3. **Fill shifts systematically**: Go day by day, ensuring coverage requirements are met

4. **Enforce sequence rules**: Ensure all shift transitions follow valid patterns (M→M/L, S→S/M/L, P→any)

5. **Respect consecutive limits**: Max 2 consecutive nights, max 5 consecutive work days

6. **Apply mandatory leave rules**: After assigning night shifts, add mandatory leave days

7. **Handle conflicts**: If mandatory leave conflicts with requested leave, requested leave takes priority

8. **Validate and balance**: Ensure all rules are followed and workload is distributed fairly



Please provide ONLY the JSON output without any explanation or additional text.

Structure the output as a single markdown block, ready to be saved as `TODO.MD`." > TODO.MD