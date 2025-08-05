curl

curl --location 'http://localhost:8000/api/generate-schedule'
--header 'Content-Type: application/json'
--data '{
"personnel": [
{
"id": 1,
"name": "Andi",
"role": "shift",
"requested_leaves": [
5
],
"extra_leaves": [],
"annual_leaves": []
},
{
"id": 2,
"name": "Budi",
"role": "shift",
"requested_leaves": [],
"extra_leaves": [],
"annual_leaves": []
},
{
"id": 3,
"name": "Citra",
"role": "shift",
"requested_leaves": [],
"extra_leaves": [],
"annual_leaves": [
29
]
},
{
"id": 4,
"name": "Dedi",
"role": "shift",
"requested_leaves": [],
"extra_leaves": [],
"annual_leaves": []
},
{
"id": 5,
"name": "Eka",
"role": "shift",
"requested_leaves": [
15
],
"extra_leaves": [],
"annual_leaves": []
},
{
"id": 6,
"name": "Gita",
"role": "shift",
"requested_leaves": [],
"extra_leaves": [],
"annual_leaves": []
},
{
"id": 7,
"name": "Hani",
"role": "shift",
"requested_leaves": [],
"extra_leaves": [],
"annual_leaves": []
},
{
"id": 8,
"name": "Indra",
"role": "shift",
"requested_leaves": [
10
],
"extra_leaves": [],
"annual_leaves": []
},
{
"id": 9,
"name": "Joko",
"role": "shift",
"requested_leaves": [],
"extra_leaves": [],
"annual_leaves": []
},
{
"id": 10,
"name": "Fani",
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
}'

response
{
"schedule": {
"2025-09-01": {
"P": [
10
],
"S": [
1,
2
],
"M": [
3,
9
]
},
"2025-09-02": {
"P": [
10
],
"S": [
6,
7
],
"M": [
2,
4
]
},
"2025-09-03": {
"P": [
10
],
"S": [
7,
8
],
"M": [
4,
9
]
},
"2025-09-04": {
"P": [
2
],
"S": [
7,
8
],
"M": [
1,
3
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
3,
8
]
},
"2025-09-06": {
"P": [
4,
9
],
"S": [
6,
7
],
"M": [
1,
2,
5
]
},
"2025-09-07": {
"P": [
3,
9
],
"S": [
4,
6
],
"M": [
1,
2,
5
]
},
"2025-09-08": {
"P": [
10
],
"S": [
4,
6
],
"M": [
7,
8
]
},
"2025-09-09": {
"P": [
2
],
"S": [
3,
9
],
"M": [
6,
7
]
},
"2025-09-10": {
"P": [
10
],
"S": [
1,
5
],
"M": [
4,
9
]
},
"2025-09-11": {
"P": [
10
],
"S": [
5,
7
],
"M": [
6,
8
]
},
"2025-09-12": {
"P": [
10
],
"S": [
3,
4
],
"M": [
6,
7
]
},
"2025-09-13": {
"P": [
2,
8
],
"S": [
1,
4
],
"M": [
3,
5,
9
]
},
"2025-09-14": {
"P": [
2,
8
],
"S": [
1,
7
],
"M": [
4,
5,
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
8
]
},
"2025-09-16": {
"P": [
6
],
"S": [
1,
5
],
"M": [
3,
7
]
},
"2025-09-17": {
"P": [
4,
9
],
"S": [
2,
5
],
"M": [
1,
6,
8
]
},
"2025-09-18": {
"P": [
10
],
"S": [
3,
5
],
"M": [
2,
8
]
},
"2025-09-19": {
"P": [
10
],
"S": [
1,
5
],
"M": [
6,
7
]
},
"2025-09-20": {
"P": [
3
],
"S": [
9
],
"M": [
1,
2,
7
]
},
"2025-09-21": {
"P": [
4,
8
],
"S": [
6,
9
],
"M": [
1,
2,
5
]
},
"2025-09-22": {
"P": [
8
],
"S": [
3,
9
],
"M": [
4,
5
]
},
"2025-09-23": {
"P": [
10
],
"S": [
3,
6
],
"M": [
1,
9
]
},
"2025-09-24": {
"P": [
10
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
"2025-09-25": {
"P": [
10
],
"S": [
1,
8
],
"M": [
6,
7
]
},
"2025-09-26": {
"P": [
10
],
"S": [
4,
9
],
"M": [
5,
8
]
},
"2025-09-27": {
"P": [
1,
3
],
"S": [
2,
4
],
"M": [
7,
8,
9
]
},
"2025-09-28": {
"P": [
5,
6
],
"S": [
2,
4
],
"M": [
1,
3,
9
]
},
"2025-09-29": {
"P": [
10
],
"S": [
2,
8
],
"M": [
4,
5
]
},
"2025-09-30": {
"P": [
7
],
"S": [
2,
8
],
"M": [
3,
6
]
}
}
}

violation
Violations Found (8):
👤 Personnel (Andi):Missing mandatory leave on day 23 after 2 consecutive nights ending on day 21
👤 Personnel (Budi):Missing mandatory leave on day 9 after 2 consecutive nights ending on day 7
👤 Personnel (Citra):Missing mandatory leave on day 7 after 2 consecutive nights ending on day 5
👤 Personnel (Citra):Missing mandatory leave on day 18 after 2 consecutive nights ending on day 16
👤 Personnel (Eka):Missing mandatory leave on day 16 after 2 consecutive nights ending on day 14
👤 Personnel (Eka):Missing mandatory leave on day 24 after 2 consecutive nights ending on day 22
👤 Personnel (Hani):Missing mandatory leave on day 11 after 2 consecutive nights ending on day 9
👤 Personnel (Indra):Missing mandatory leave on day 29 after 2 consecutive nights ending on day 27

kayaknya masalahnya tinggal mandatory leave after 2 consecutive night.

adjust dikit lagi aja disitu.

