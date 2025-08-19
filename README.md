# Mini Leave Management System — FastAPI (MVP)

A clean, minimal Leave Management MVP with core flows:
- Add employee
- Apply for leave
- Approve / Reject leave
- Fetch leave balance

## Tech Stack
- **Backend**: FastAPI + SQLAlchemy (SQLite)
- **Language**: Python 3.10+

## Project Layout
```
leave_management_mini/
├─ backend/
│  ├─ main.py
│  ├─ models.py
│  ├─ schemas.py
│  └─ database.py
├─ diagrams/
│  └─ HLD.md
├─ tests/
│  └─ scenarios.md
├─ requirements.txt
└─ README.md
```

## Setup (Local)
1. Create & activate a virtualenv (recommended).
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the API:
   ```bash
   uvicorn backend.main:app --reload
   ```
4. Open docs: http://127.0.0.1:8000/docs

## Default Rules / Assumptions
- Annual leave quota: **30 calendar days per year** (configurable via code constant).
- Days counted as **inclusive calendar days** (no holiday/weekend logic in MVP).
- Overlap is not allowed with **PENDING** or **APPROVED** leaves.
- Balance is checked at **application time** and **approval time**.
- Multi-year spanning requests are clipped per-year for balance reporting.

## API Endpoints (Sample)

### 1) Add Employee
`POST /employees`
```json
{
  "name": "Ribu Kumar",
  "email": "ribu@example.com",
  "department": "Engineering",
  "joining_date": "2025-01-01"
}
```

### 2) Apply for Leave
`POST /leaves`
```json
{
  "employee_id": 1,
  "start_date": "2025-01-15",
  "end_date": "2025-01-18",
  "reason": "Medical"
}
```

### 3) Decide Leave (Approve / Reject)
`POST /leaves/{leave_id}/decision`
```json
{
  "status": "APPROVED"
}
```

### 4) Leave Balance
`GET /employees/{employee_id}/leave-balance?year=2025`

### 5) List Leaves
`GET /leaves?employee_id=1&status=PENDING`

## Edge Cases Handled
- Applying before joining date → **400**
- End date before start date → **400**
- Overlapping requests with existing PENDING/APPROVED → **400**
- Excess days beyond remaining balance → **400**
- Employee/Leave not found → **404**
- Duplicate email on employee creation → **400**

## Testing Quickly (cURL)
```bash
# 1) Add employee
curl -X POST http://127.0.0.1:8000/employees -H "Content-Type: application/json" -d '
{"name":"Alice","email":"alice@corp.com","department":"HR","joining_date":"2025-01-01"}'

# 2) Apply leave
curl -X POST http://127.0.0.1:8000/leaves -H "Content-Type: application/json" -d '
{"employee_id":1,"start_date":"2025-01-10","end_date":"2025-01-12","reason":"Personal"}'

# 3) Approve
curl -X POST http://127.0.0.1:8000/leaves/1/decision -H "Content-Type: application/json" -d '
{"status":"APPROVED"}'

# 4) Balance
curl "http://127.0.0.1:8000/employees/1/leave-balance?year=2025"

# 5) List
curl "http://127.0.0.1:8000/leaves?employee_id=1"
```

## Deployment (Render - Free Tier)
1. Create a new Web Service pointing to this repo.
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Add a **Render PostgreSQL** later if you want to move off SQLite.

### Heroku (if available)
Add a `Procfile`:
```
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

## Potential Improvements
- Role-based access control (Employee vs HR Admin).
- Half-day leaves and working-day calendar logic.
- Email/Slack notifications on status change.
- Leave types (Casual/Sick/Unpaid), carry-forward and accrual.
- Reporting & exports, audit logs.
- Auth (JWT) and user accounts.