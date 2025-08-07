curl --location 'http://localhost:8000/api/generate-schedule' \
--header 'Content-Type: application/json' \
--data '{
    "personnel": [
        {
            "id": 1,
            "name": "dr. LARAS W",
            "role": "shift",
            "requested_leaves": [],
            "extra_leaves": [],
            "annual_leaves": []
        },
        {
            "id": 2,
            "name": "dr. SITI AISYAH",
            "role": "shift",
            "requested_leaves": [
                6,
                7
            ],
            "extra_leaves": [
                12,
                13,
                14,
                27,
                28
            ],
            "annual_leaves": []
        },
        {
            "id": 3,
            "name": "dr. RABIATUL H",
            "role": "shift",
            "requested_leaves": [],
            "extra_leaves": [],
            "annual_leaves": []
        },
        {
            "id": 4,
            "name": "dr. ADIE K",
            "role": "shift",
            "requested_leaves": [],
            "extra_leaves": [
                25,
                26,
                27
            ],
            "annual_leaves": []
        },
        {
            "id": 5,
            "name": "dr. LOKOT",
            "role": "shift",
            "requested_leaves": [
                9,
                10
            ],
            "extra_leaves": [
                11,
                12,
                13,
                14,
                15
            ],
            "annual_leaves": []
        },
        {
            "id": 6,
            "name": "dr. VENEZIA A",
            "role": "shift",
            "requested_leaves": [
                16,
                17
            ],
            "extra_leaves": [
                18,
                19
            ],
            "annual_leaves": []
        },
        {
            "id": 7,
            "name": "dr. ANINDA",
            "role": "shift",
            "requested_leaves": [],
            "extra_leaves": [
                20,
                21,
                22
            ],
            "annual_leaves": []
        },
        {
            "id": 8,
            "name": "dr. GRACYA",
            "role": "shift",
            "requested_leaves": [
                4,
                5,
                17,
                18
            ],
            "extra_leaves": [
                6
            ],
            "annual_leaves": []
        },
        {
            "id": 9,
            "name": "dr. ANISA A",
            "role": "shift",
            "requested_leaves": [
                21,
                22
            ],
            "extra_leaves": [
                1,
                2,
                3,
                4,
                23,
                24
            ],
            "annual_leaves": []
        },
        {
            "id": 10,
            "name": "NON_SHIFT_1",
            "role": "non_shift",
            "requested_leaves": [],
            "extra_leaves": [],
            "annual_leaves": []
        }
    ],
    "config": {
        "month": "2025-09",
        "public_holidays": [
            17
        ],
        "special_dates": {
            "2025-09-20": {
                "P": 1,
                "S": 1,
                "M": 3
            }
        },
        "max_night_shifts": 9,
        "max_default_leaves": 10
    }
}
'

---
Enfeasible (error)
{
    "detail": {
        "error": "INFEASIBLE",
        "message": "The scheduling constraints cannot be satisfied with the given parameters.",
        "suggestions": [
            "Reduce the number of requested leaves",
            "Increase the number of personnel",
            "Adjust shift requirements for special dates",
            "Check for conflicting leave requests"
        ]
    }
}
Http status code: 422 Unprocessable Entity

---
Success
{
    "schedule": {
        "2025-09-01": {
            "P": [
                7
            ],
            "S": [
                3,
                5
            ],
            "M": [
                2,
                4
            ]
        },
        "2025-09-02": {
            "P": [
                10
            ],
            "S": [
                5,
                6
            ],
            "M": [
                7,
                8
            ]
        },
        "2025-09-03": {
            "P": [
                10
            ],
            "S": [
                3,
                5
            ],
            "M": [
                4,
                8
            ]
        },
        "2025-09-04": {
            "P": [
                1
            ],
            "S": [
                2,
                6
            ],
            "M": [
                3,
                7
            ]
        },
        "2025-09-05": {
            "P": [
                10
            ],
            "S": [
                5,
                6
            ],
            "M": [
                2,
                9
            ]
        },
        "2025-09-06": {
            "P": [
                3,
                7
            ],
            "S": [
                1,
                6
            ],
            "M": [
                4,
                5,
                9
            ]
        },
        "2025-09-07": {
            "P": [
                7,
                8
            ],
            "S": [
                1,
                3
            ],
            "M": [
                4,
                5,
                6
            ]
        },
        "2025-09-08": {
            "P": [
                10
            ],
            "S": [
                7,
                8
            ],
            "M": [
                1,
                6
            ]
        },
        "2025-09-09": {
            "P": [
                10
            ],
            "S": [
                2,
                8
            ],
            "M": [
                3,
                7
            ]
        },
        "2025-09-10": {
            "P": [
                10
            ],
            "S": [
                8,
                9
            ],
            "M": [
                2,
                4
            ]
        },
        "2025-09-11": {
            "P": [
                10
            ],
            "S": [
                3,
                9
            ],
            "M": [
                1,
                6
            ]
        },
        "2025-09-12": {
            "P": [
                10
            ],
            "S": [
                4,
                9
            ],
            "M": [
                3,
                8
            ]
        },
        "2025-09-13": {
            "P": [
                1,
                6
            ],
            "S": [
                2,
                7
            ],
            "M": [
                4,
                8,
                9
            ]
        },
        "2025-09-14": {
            "P": [
                1,
                3
            ],
            "S": [
                2,
                7
            ],
            "M": [
                4,
                6,
                9
            ]
        },
        "2025-09-15": {
            "P": [
                10
            ],
            "S": [
                1,
                7
            ],
            "M": [
                3,
                6
            ]
        },
        "2025-09-16": {
            "P": [
                10
            ],
            "S": [
                2,
                5
            ],
            "M": [
                7,
                8
            ]
        },
        "2025-09-17": {
            "P": [
                3,
                4
            ],
            "S": [
                2,
                9
            ],
            "M": [
                1,
                5,
                7
            ]
        },
        "2025-09-18": {
            "P": [
                10
            ],
            "S": [
                2,
                9
            ],
            "M": [
                3,
                4
            ]
        },
        "2025-09-19": {
            "P": [
                10
            ],
            "S": [
                5,
                8
            ],
            "M": [
                1,
                9
            ]
        },
        "2025-09-20": {
            "P": [
                4,
                6
            ],
            "S": [
                2,
                5
            ],
            "M": [
                3,
                8,
                9
            ]
        },
        "2025-09-21": {
            "P": [
                4,
                6
            ],
            "S": [
                1,
                2
            ],
            "M": [
                3,
                5,
                8
            ]
        },
        "2025-09-22": {
            "P": [
                10
            ],
            "S": [
                1,
                4
            ],
            "M": [
                2,
                5
            ]
        },
        "2025-09-23": {
            "P": [
                10
            ],
            "S": [
                4,
                6
            ],
            "M": [
                1,
                7
            ]
        },
        "2025-09-24": {
            "P": [
                10
            ],
            "S": [
                2,
                8
            ],
            "M": [
                1,
                6
            ]
        },
        "2025-09-25": {
            "P": [
                7
            ],
            "S": [
                2,
                3
            ],
            "M": [
                5,
                8
            ]
        },
        "2025-09-26": {
            "P": [
                7
            ],
            "S": [
                6,
                9
            ],
            "M": [
                2,
                3
            ]
        },
        "2025-09-27": {
            "P": [
                1,
                5
            ],
            "S": [
                8,
                9
            ],
            "M": [
                2,
                6,
                7
            ]
        },
        "2025-09-28": {
            "P": [
                1,
                4
            ],
            "S": [
                3,
                9
            ],
            "M": [
                5,
                6,
                7
            ]
        },
        "2025-09-29": {
            "P": [
                10
            ],
            "S": [
                4,
                8
            ],
            "M": [
                5,
                9
            ]
        },
        "2025-09-30": {
            "P": [
                10
            ],
            "S": [
                4,
                8
            ],
            "M": [
                1,
                9
            ]
        }
    }
}